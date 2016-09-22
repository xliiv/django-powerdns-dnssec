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


class ServiceStatus(Enum):
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'


class OwnershipType(Enum):
    BO = 'Business Owner'
    TO = 'Technical Owner'


class Service(TimeTrackable):
    name = models.CharField(_("name"), max_length=255)
    uid = models.CharField(max_length=100, unique=True, db_index=True)
    status = models.CharField(
        max_length=100, db_index=True,
        choices=[(status.name, status.value) for status in ServiceStatus]
    )
    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='ServiceOwner'
    )

    def __str__(self):
        return '{} {} ({})'.format(self.name, self.status, self.uid)


class ServiceOwner(TimeTrackable):
    service = models.ForeignKey(Service)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    ownership_type = models.CharField(
        max_length=10, db_index=True,
        choices=[(type_.name, type_.value) for type_ in OwnershipType],
    )

    def __str__(self):
        return '{} - {} ({})'.format(
            self.user, self.service, self.ownership_type,
        )


class OwnershipByService(models.Model):

    class Meta:
        abstract = True

    service = models.ForeignKey(Service, blank=True, null=True)
