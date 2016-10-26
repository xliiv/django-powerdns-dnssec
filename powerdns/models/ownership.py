"""
This module provide a new way of ownership/permission to Domains and Records.

The main concept of this is:
    - all Domains and Records belongs to a Service
    - Service has owners
    - Permissions to adding/editing/deleting Domains and Records comes from
        this ownership
"""

from enum import Enum

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from powerdns.utils import TimeTrackable


class OwnershipType(Enum):
    BO = 'Business Owner'
    TO = 'Technical Owner'


class Service(TimeTrackable):
    name = models.CharField(_("name"), max_length=255)
    uid = models.CharField(max_length=100, unique=True, db_index=True)
    is_active = models.BooleanField(null=False, default=True)
    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='ServiceOwner',
        related_name='service_owners',
    )

    def __str__(self):
        return '{} {} ({})'.format(self.name, self.is_active, self.uid)


class ServiceOwner(TimeTrackable):
    service = models.ForeignKey(Service)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    ownership_type = models.CharField(
        max_length=10, db_index=True,
        choices=[(type_.name, type_.value) for type_ in OwnershipType],
    )

    def __str__(self):
        return '{} - {} ({})'.format(
            self.owner, self.service, self.ownership_type,
        )


class OwnershipByService(models.Model):

    class Meta:
        abstract = True

    service = models.ForeignKey(Service, blank=True, null=True)

    def _has_access_by_service(self, user):
        "Check if user is one of owners of service assigned to this model."
        if self.service:
            permission_by_service = (
                user.id in self.service.owners.values_list('id', flat=True)
            )
        else:
            permission_by_service = False
        return permission_by_service
