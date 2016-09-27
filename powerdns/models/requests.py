"""Model for change requests"""

import logging

from django.db import models, transaction
from django.conf import settings
from django_extensions.db.fields.json import JSONField
from dj.choices import Choices
from dj.choices.fields import ChoiceField
from django.contrib.contenttypes.fields import ContentType, GenericForeignKey
from django.utils.translation import ugettext_lazy as _
from threadlocals.threadlocals import get_current_user
import rules

from powerdns.models import (
    validate_domain_name,
    Owned,
    Domain,
    Record
)
from powerdns.utils import AutoPtrOptions, RecordLike, flat_dict_diff


log = logging.getLogger(__name__)


def can_auto_accept_record_request(user_request, user, action):
    """
    Return True if `user_request` (RecordRequest or Record DeleteRequest) being
    done by `user` can be auto accepted for `action`.

    Skipping corner cases (included in code below) this checks:
        - if user has access to Record AND
        - if user has access to Domain (which Record belongs to)
    """
    def _validate_domain(domain):
        if not domain:
            raise Exception(
                "Can't check auto acceptance without domain set"
            )

    can_auto_accept = False
    domain = (
        user_request.domain
        if action != 'delete' else user_request.target.domain
    )
    _validate_domain(domain)
    if action == 'create':
        can_auto_accept = user_request.domain.can_auto_accept(user)
    elif action == 'update':
        can_auto_accept = (
            user_request.domain.can_auto_accept(user) and
            user_request.record.can_auto_accept(user)
        )
    elif action == 'delete':
        can_auto_accept = (
            user_request.target.domain.can_auto_accept(user) and
            user_request.target.can_auto_accept(user)
        )
    return can_auto_accept


class RequestStates(Choices):
    _ = Choices.Choice
    OPEN = _('Open')
    ACCEPTED = _('Accepted')
    REJECTED = _('Rejected')


class Request(Owned):
    """Abstract request"""

    class Meta:
        abstract = True

    state = ChoiceField(
        choices=RequestStates,
        default=RequestStates.OPEN,
    )
    key = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )
    last_change_json = JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.owner is None:
            self.owner = get_current_user()
        super().save(*args, **kwargs)

    def _log_processed_request_message(self):
        log.warning('{} (id:{}) already {}'.format(
            self._meta.object_name,
            self.id,
            RequestStates.DescFromID(self.state).lower(),
        ))


class DeleteRequest(Request):
    """A request for object deletion"""
    content_type = models.ForeignKey(ContentType)
    target_id = models.PositiveIntegerField()
    target = GenericForeignKey('content_type', 'target_id')

    @transaction.atomic
    def accept(self):
        if self.state != RequestStates.OPEN:
            self._log_processed_request_message()
            return

        old_dict = self.target.as_history_dump()
        new_dict = self.target.as_empty_history()
        result = flat_dict_diff(old_dict, new_dict)
        result['_request_type'] = 'delete'
        self.last_change_json = result

        self.target.delete()
        self.state = RequestStates.ACCEPTED
        self.save()

    @transaction.atomic
    def reject(self):
        """Reject the request"""
        if self.state != RequestStates.OPEN:
            self._log_processed_request_message()
            return
        self.state = RequestStates.REJECTED
        self.save()

    def __str__(self):
        return 'Delete {}'.format(self.target)


rules.add_perm('powerdns.add_deleterequest', rules.is_authenticated)


class ChangeCreateRequest(Request):
    """Abstract change/create request"""

    ignore_fields = {'created', 'modified'}
    prefix = 'target_'

    class Meta:
        abstract = True

    def _get_json_history(self, object_):
        if object_.id:
            # udpate
            old_dict = object_.as_history_dump()
        else:
            # creation
            old_dict = object_.as_empty_history()
        new_dict = self.as_history_dump()
        result = flat_dict_diff(old_dict, new_dict)
        result['_request_type'] = 'update' if object_.id else 'create'
        return result

    def _set_json_history(self, object_):
        self.last_change_json = self._get_json_history(object_)

    @transaction.atomic
    def accept(self):
        object_ = self.get_object()
        if self.state != RequestStates.OPEN:
            self._log_processed_request_message()
            return object_

        self._set_json_history(object_)
        for field_name in type(self).copy_fields:
            if field_name in self.ignore_fields:
                continue
            if field_name == 'target_owner' and not getattr(self, field_name):
                continue
            setattr(
                object_,
                field_name[len(self.prefix):],
                getattr(self, field_name)
            )
        object_.save()
        self.assign_object(object_)
        self.state = RequestStates.ACCEPTED
        self.save()
        return object_

    @transaction.atomic
    def reject(self):
        """Reject the request"""
        if self.state != RequestStates.OPEN:
            self._log_processed_request_message()
            return
        object_ = self.get_object()
        self._set_json_history(object_)
        self.state = RequestStates.REJECTED
        self.save()

    def copy_records_data(self, fields_to_copy):
        """Sets data from `fields_to_copy` on self

        args:
            fields_to_copy: [(key, value), ..]
        """
        all_fields = self._meta.get_all_field_names()
        for field_name, value in fields_to_copy:
            if field_name in all_fields:
                setattr(self, field_name, value)
            elif 'target_' + field_name in all_fields:
                setattr(self, 'target_' + field_name, value)
            else:
                log.warning("Unknown field")


class DomainRequest(ChangeCreateRequest):
    """Request for domain creation/modification"""

    copy_fields = [
        'target_name',
        'target_master',
        'target_type',
        'target_account',
        'target_remarks',
        'target_template',
        'target_reverse_template',
        'target_auto_ptr',
        'target_owner',
    ]

    domain = models.ForeignKey(
        Domain,
        related_name='requests',
        null=True,
        blank=True,
        help_text=_(
            'The domain for which a change is requested'
        ),
    )
    parent_domain = models.ForeignKey(
        Domain,
        related_name='child_requests',
        null=True,
        blank=True,
        help_text=_(
            'The parent domain for which a new subdomain is to be created'
        ),

    )
    target_name = models.CharField(
        _("name"),
        max_length=255,
        validators=[validate_domain_name],
        blank=False,
        null=False,
    )
    target_master = models.CharField(
        _("master"), max_length=128, blank=True, null=True,
    )
    target_type = models.CharField(
        _("type"),
        max_length=6,
        blank=True,
        null=True,
        choices=Domain.DOMAIN_TYPE,
    )
    target_account = models.CharField(
        _("account"), max_length=40, blank=True, null=True,
    )
    target_remarks = models.TextField(_('Additional remarks'), blank=True)
    target_template = models.ForeignKey(
        'powerdns.DomainTemplate',
        verbose_name=_('Template'),
        blank=True,
        null=True,
        related_name='template_for_requests'
    )
    target_reverse_template = models.ForeignKey(
        'powerdns.DomainTemplate',
        verbose_name=_('Reverse template'),
        blank=True,
        null=True,
        related_name='reverse_template_for_requests',
        help_text=_(
            'A template that should be used for reverse domains when '
            'PTR templates are automatically created for A records in this '
            'template.'
        )
    )
    target_auto_ptr = ChoiceField(
        choices=AutoPtrOptions,
        default=AutoPtrOptions.ALWAYS,
        help_text=_(
            'Should A records have auto PTR by default'
        )
    )
    target_unrestricted = models.BooleanField(
        _('Unrestricted'),
        null=False,
        default=False,
        help_text=_(
            "Can users that are not owners of this domain add records"
            "to it without owner's permission?"
        )
    )
    target_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Owner'),
        null=True,  # For the sake of existing ones
        blank=False,
        related_name='+',

    )

    def __str__(self):
        return self.target_name

    def get_object(self):
        if self.domain is not None:
            return self.domain
        else:
            return Domain()

    def assign_object(self, obj):
        self.domain = obj

    def as_history_dump(self):
        """We don't care about domain history for now"""
        return {}


# rules.add_perm('powerdns', rules.is_authenticated)
rules.add_perm('powerdns.add_domainrequest', rules.is_authenticated)


class RecordRequest(ChangeCreateRequest, RecordLike):

    copy_fields = [
        'target_name',
        'target_type',
        'target_content',
        'target_prio',
        'target_auth',
        'target_disabled',
        'target_remarks',
        'target_ttl',
        'target_owner',
    ]

    domain = models.ForeignKey(
        Domain,
        related_name='record_requests',
        null=False,
        help_text=_(
            'The domain for which a record is to be added'
        ),
    )
    record = models.ForeignKey(
        Record,
        # these two used for history purpose
        on_delete=models.DO_NOTHING, db_constraint=False,
        related_name='requests',
        null=True,
        blank=True,
        help_text=_(
            'The record for which a change is being requested'
        ),
    )
    target_name = models.CharField(
        _("name"), max_length=255, blank=False, null=False,
        validators=[validate_domain_name],
        help_text=_("Actual name of a record. Must not end in a '.' and be"
                    " fully qualified - it is not relative to the name of the"
                    " domain!"),
    )
    target_type = models.CharField(
        _("type"), max_length=6, blank=False, null=False,
        choices=Record.RECORD_TYPE, help_text=_("Record qtype"),
    )
    target_content = models.CharField(
        _("content"), max_length=255, blank=True, null=True,
        help_text=_("The 'right hand side' of a DNS record. For an A"
                    " record, this is the IP address"),
    )
    target_ttl = models.PositiveIntegerField(
        _("TTL"), blank=True, null=True, default=3600,
        help_text=_("TTL in seconds"),
    )
    target_prio = models.PositiveIntegerField(
        _("priority"), blank=True, null=True,
        help_text=_("For MX records, this should be the priority of the"
                    " mail exchanger specified"),
    )
    target_auth = models.NullBooleanField(
        _("authoritative"),
        help_text=_("Should be set for data for which is itself"
                    " authoritative, which includes the SOA record and our own"
                    " NS records but not set for NS records which are used for"
                    " delegation or any delegation related glue (A, AAAA)"
                    " records"),
        default=True,
    )
    target_disabled = models.BooleanField(
        _("Disabled"),
        help_text=_(
            "This record should not be used for actual DNS queries."
            " Note - this field works for pdns >= 3.4.0"
        ),
        default=False,
    )

    target_remarks = models.TextField(blank=True)
    target_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('Owner'),
        null=True,  # For the sake of existing ones
        blank=False,
        related_name='+',
    )

    def get_record_pk(self):
        if self.record:
            return self.record.pk

    def __str__(self):
        if self.target_prio is not None:
            content = "%d %s" % (self.target_prio, self.target_content)
        else:
            content = self.target_content
        return "%s IN %s %s" % (self.target_name, self.target_type, content)

    def get_object(self):
        if self.record is not None:
            return self.record
        else:
            return Record(domain=self.domain, owner=self.owner)

    def assign_object(self, obj):
        self.record = obj

    def as_history_dump(self):
        return {
            'content': self.target_content or '',
            'name': self.target_name or '',
            'owner': getattr(self.target_owner, 'username', ''),
            'prio': self.target_prio or '',
            'remarks': self.target_remarks or '',
            'ttl':  self.target_ttl or '',
            'type':  self.target_type or '',
        }


rules.add_perm('powerdns.add_recordrequest', rules.is_authenticated)
