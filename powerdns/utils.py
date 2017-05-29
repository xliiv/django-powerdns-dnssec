"""Utilities for powerdns models"""

import ipaddress

import rules
from django import VERSION
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.core.validators import (
    validate_ipv4_address,
    validate_ipv6_address,
    RegexValidator
)
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from threadlocals.threadlocals import get_current_user
from dj.choices import Choices


DOMAIN_NAME_RECORDS = ('CNAME', 'MX', 'NAPTR', 'NS', 'PTR')


# Validator for the domain names only in RFC-1035
# PowerDNS considers the whole zone to be invalid if any of the records end
# with a period so this custom validator is used to catch them


# Valid: example.com
# Valid: *.example.com
# Invalid: example.com.
# Invalid: ex*mple.com
validate_domain_name = RegexValidator(
    r'^(\*\.)?([_A-Za-z0-9-]+\.)*([A-Za-z0-9])+$'
)


validate_dn_optional_dot = RegexValidator(
    '^[A-Za-z0-9.-]*$'
)


validate_time = RegexValidator('^[0-9]+$')


def validate_name_equal_to_content(name, content):
    """Validator checks if record name is not equal to content

    In theory NS record can contain same name and content, and with
    glue record configuration it will work. However it is not good
    practice so we are not allowing such configuration.
    """
    if name == content:
        raise ValidationError(
            'Cannot create record with the same name and content'
        )


def validate_soa(value):
    """Validator for a correct SOA record"""
    try:
        name, email, sn, refresh, retry, expiry, nx = value.split()
    except ValueError:
        raise ValidationError(_('Enter a valid SOA record'))
    for subvalue, field in [
        (name, 'Domain name'),
        (email, 'e-mail'),
    ]:
        try:
            validate_dn_optional_dot(subvalue)
        except ValidationError:
            raise ValidationError(
                _('Incorrect {}. Should be a valid domain name.'.format(
                    field
                ))
            )
    for subvalue, field in [
        (sn, 'Serial'),
        (refresh, 'Refresh rate'),
        (retry, 'Retry rate'),
        (expiry, 'Expiry time'),
        (nx, 'Negative resp. time'),
    ]:
        try:
            validate_time(subvalue)
        except ValidationError:
            raise ValidationError(
                _('Incorrect {}. Should be a valid domain name.'.format(
                    field
                ))
            )

# Due to the idiotic way permissions work in admin, we need to give users
# generic 'change' view (so they see the changelist), bo no generic 'delete'
# view (so they can't bulk-delete).


@rules.predicate
def no_object(user, object_):
    return object_ is None


@rules.predicate
def is_owner(user, object_):
    return object_ and object_.owner == user


@rules.predicate
def is_authorised(user, object_):
    return object_ and user in (
        authorisation.authorised
        for authorisation in object_.authorisations.all()
    )
    return not object_ or object_.owner == user


class TimeTrackable(models.Model):
    created = models.DateTimeField(
        verbose_name=_("date created"), auto_now=False, auto_now_add=True,
        editable=False,
    )
    modified = models.DateTimeField(
        verbose_name=_('last modified'), auto_now=True, editable=False,
    )

    class Meta:
        abstract = True


class Owned(models.Model):
    """
    DEPRECATED in favour of `powerdns.models.ownership` module.

    Model that has an owner. This owner is set as default to the creator
    of this model, but can be overridden.
    """

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    authorisations = GenericRelation(
        'Authorisation',
        object_id_field='target_id'
    )

    class Meta:
        abstract = True

    def email_owner(self, creator):
        """If the owner is different from the creator - notify the owner."""
        if (
            creator != self.owner and
            settings.ENABLE_OWNER_NOTIFICATIONS and
            hasattr(self.owner, 'email')
        ):
            subject_template, content_template = settings.OWNER_NOTIFICATIONS[
                type(self)._meta.object_name
            ]
            kwargs = {}
            for key, user in [
                ('owner', self.owner),
                ('creator', creator),
            ]:
                kwargs[key + '-email'] = user.email
                kwargs[key + '-name'] = '{} {}'.format(
                    user.first_name,
                    user.last_name
                )
            kwargs['object'] = str(self)

            subject = subject_template.format(**kwargs)
            content = content_template.format(**kwargs)
            send_mail(
                subject,
                content,
                settings.FROM_EMAIL,
                [self.owner.email],
            )


class PermissionValidator():
    """A validator that only allows objects that user has permission for"""

    def __init__(self, permission, *args, **kwargs):
        self.permission = permission
        super().__init__(*args, **kwargs)

    def __call__(self, object_):
        from .models import can_edit
        if not can_edit(get_current_user(), object_):
            raise ValidationError("You don't have permission to use this")
        return object_


class DomainForRecordValidator(PermissionValidator):
    """A validator for 'domain' field in record forms and API"""
    def __init__(self, *args, **kwargs):
        super().__init__('powerdns.change_domain', *args, **kwargs)

    def __call__(self, object_):
        if object_.unrestricted:
            return object_
        else:
            return super().__call__(object_)


# TODO(mkurek): rename to sth better
def to_reverse(ip):
    """
    Given an ip address it will return a tuple of (domain, number)
    suitable for PTR record

    Example:
    >>> to_reverse('192.168.1.2')
    ('2', '1.1.168.192.in-addr.arpa')
    >>> to_reverse('2001:0db8:0:0::1428:57ab')
    ('b', 'a.7.5.8.2.4.1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa')  # noqa
    """
    return _reverse_ip(ip)


def reverse_pointer(ip):
    """
    Return reversed IP address in PTR format. Handles IPv4 and IPv6.

    Example:
    >>> reverse_pointer('192.168.1.2')
    '2.1.1.168.192.in-addr.arpa'
    >>> reverse_pointer('2001:0db8:0:0::1428:57ab')
    'b.a.7.5.8.2.4.1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa'
    """
    return '.'.join(_reverse_ip(ip))


def _reverse_ip(ip):
    """
    Reverse `ip` to ptr.

    Returns: tuple of (last_byte, domain) suitable for PTR record
    last_byte is the last byte of IPv4 address and last character of IPv6
    address

    Example:
    >>> _reverse_ip('192.168.1.2')
    ('2', '1.1.168.192.in-addr.arpa')
    >>> _reverse_ip('2001:0db8:0:0::1428:57ab')
    ('b', 'a.7.5.8.2.4.1.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.8.b.d.0.1.0.0.2.ip6.arpa')  # noqa
    """
    ip_obj = ipaddress.ip_address(ip)
    if isinstance(ip_obj, ipaddress.IPv6Address):
        last_byte, *first_bytes_reversed = ip_obj.exploded[::-1].replace(':', '')  # noqa
        domain_suffix = 'ip6.arpa'
    else:
        last_byte, *first_bytes_reversed = str(ip_obj).split('.')[::-1]
        domain_suffix = 'in-addr.arpa'
    return last_byte, '.'.join(first_bytes_reversed + [domain_suffix])


class AutoPtrOptions(Choices):
    _ = Choices.Choice
    NEVER = _("Never")
    ALWAYS = _("Always")
    ONLY_IF_DOMAIN = _("Only if domain exists")


DOMAIN_TYPE = (
    ('MASTER', 'MASTER'),
    ('NATIVE', 'NATIVE'),
    ('SLAVE', 'SLAVE'),
)


def format_recursive(template, arguments):
    """
    Performs str.format on the template in a recursive fashion iterating over
    lists and dictionary values

    >>> template = {
    ... 'a': 'Value {a}',
    ... 'b': {
    ...     'a': 'Value {a}',
    ...     'b': 'Value {b}',
    ... },
    ... 'c': ['Value {a}', 'Value {b}'],
    ... 'd': 10,
    ... }
    >>> arguments = {
    ... 'a': 'A',
    ... 'b': 'B',
    ... }
    >>> result = format_recursive(template, arguments)
    >>> result['a']
    'Value A'
    >>> result['b']['b']
    'Value B'
    >>> result['c'][0]
    'Value A'
    >>> result['d']
    10
    """
    if isinstance(template, str):
        return template.format(**arguments)
    elif isinstance(template, dict):
        return {
            k: format_recursive(v, arguments)
            for (k, v) in template.items()
        }
    elif isinstance(template, list):
        return [format_recursive(v, arguments) for v in template]
    else:
        return template


class RecordLike(models.Model):
    """Object validated like a record"""

    class Meta:
        abstract = True

    def get_field(self, name):
        """Get the value of a prefixed or not field"""
        return getattr(self, self.prefix + name)

    def set_field(self, name, value):
        """Set the value of a prefixed or not field"""
        return setattr(self, self.prefix + name, value)

    def clean(self):
        self.clean_content_field()
        self.force_case()
        self.validate_for_conflicts()
        return super(RecordLike, self).clean()

    def clean_content_field(self):
        """Perform a type-dependent validation of content field"""
        type_ = self.get_field('type')
        content = self.get_field('content')
        if type_ == 'A':
            validate_ipv4_address(content)
        elif type_ == 'AAAA':
            validate_ipv6_address(content)
        elif type_ == 'SOA':
            validate_soa(content)
        elif type_ in DOMAIN_NAME_RECORDS:
            validate_domain_name(content)
            validate_name_equal_to_content(self.get_field('name'), content)

    def validate_for_conflicts(self):
        """Ensure this record doesn't conflict with other records."""
        from .models import Record

        def check_unique(comment, **kwargs):
            conflicting = Record.objects.filter(**kwargs)
            record_pk = self.get_record_pk()
            if record_pk is not None:
                conflicting = conflicting.exclude(pk=record_pk)
            if conflicting:
                raise ValidationError(comment.format(
                    ', '.join(str(record.id) for record in conflicting)
                ))
        if self.get_field('type') == 'CNAME':
            check_unique(
                'Cannot create CNAME record. Following conflicting '
                'records exist: {}',
                name=self.get_field('name'),
            )
        else:
            check_unique(
                'Cannot create a record. Following conflicting CNAME'
                'record exists: {}',
                type='CNAME',
                name=self.get_field('name'),
            )

    def force_case(self):
        """Force the name and content case to upper and lower respectively"""
        if self.get_field('name'):
            self.set_field('name', self.get_field('name').lower())
        if self.get_field('type'):
            self.set_field('type', self.get_field('type').upper())


def flat_dict_diff(old_dict, new_dict):
    """
    return: {
        'name': {'old': 'old-value', 'new': 'new-value'},
        'ttl': {'old': 'old-value', 'new': ''},
        'prio': {'old': '', 'new': 'new-value'},
        ..
    }
    """
    def _fmt(old, new):
        return {
            'old': old,
            'new': new,
        }

    diff_result = {}
    keys = set(old_dict) & set(new_dict)
    for key in keys:
        diff_result[key] = _fmt(old_dict[key], new_dict[key])
    return diff_result


def hostname2domain(hostname):
    """
    Find longest existing domain within `hostname` or None

    Example:
        hostname = sub-domain.on.existing-domain.com
        and only existing-domain.com exists
    Then it returns `existing-domain.com` as db object.
    """
    from .models import Domain

    domain = None
    parts = hostname.split('.')
    while parts:
        try:
            domain = Domain.objects.get(name='.'.join(parts))
            break
        except Domain.DoesNotExist:
            pass
        parts = parts[1:]
    return domain


def patterns(prefix, *args):
    if VERSION < (1, 9):
        from django.conf.urls import patterns as django_patterns
        return django_patterns(prefix, *args)
    elif prefix != '':
        raise Exception("You need to update your URLConf to be a list of URL "
                        "objects")
    else:
        return list(args)


def get_matching_domains(base_domain_name):
    """
    Returns matching to provided name Domain object instances.

    Example:
    >>> get_matching_domains(30.20.10.in-addr.arpa)
    [
        <Domain: 30.20.10.in-addr.arpa>, <Domain: 20.10.in-addr.arpa>,
        <Domain: 10.in-addr.arpa>
    ]
    """
    from powerdns.models import Domain

    q_filters = Q(name__exact=base_domain_name)
    chunks = base_domain_name.split('.')[1:-2]
    suffix = '.'.join(base_domain_name.split('.')[-2:])

    for i, chunk in enumerate(chunks):
        dn = '{content}.{suffix}'.format(
            content='.'.join(chunks[i:]),
            suffix=suffix
        )
        q_filters |= Q(name__exact=dn)

    matching_domains = Domain.objects.filter(q_filters)
    matching_domains = sorted(
        matching_domains, key=lambda domain: len(domain.name), reverse=True
    )
    return matching_domains
