# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def dnsaas_records_creation(apps, schema_editor):
    """
    Creates DNSaaSRecord for every Record.
    """
    apps.get_model('powerdns', 'DNSaaSRecord').objects.all()
    for record in apps.get_model('powerdns', 'Record').objects.filter(
        dnsaasrecord=None
    ).all():
        dnsaas_record = apps.get_model('powerdns', 'DNSaaSRecord').objects.create(
            **record.__dict__
        )
        dnsaas_record.record_ptr = record
    raise Exception("TODO")


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0025_dnsaasrecord'),
    ]

    operations = [
        migrations.RunPython(dnsaas_records_creation)
    ]
