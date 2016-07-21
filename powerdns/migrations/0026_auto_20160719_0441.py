# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from powerdns.models.powerdns import _create_dnsaas_record


def dnsaas_records_creation(apps, schema_editor):
    """
    Creates DNSaaSRecord for every Record.
    """
    apps.get_model('powerdns', 'DNSaaSRecord').objects.all()
    for record in apps.get_model('powerdns', 'Record').objects.filter(
        dnsaasrecord=None
    ).all():
        print()
        print(apps.get_model('powerdns', 'Record').objects.count())
        print(apps.get_model('powerdns', 'DNSaaSRecord').objects.count())

        _create_dnsaas_record(record)
        print(apps.get_model('powerdns', 'Record').objects.count())
        print(apps.get_model('powerdns', 'DNSaaSRecord').objects.count())

        import ipdb
        ipdb.set_trace()
    raise Exception("TODO")


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0025_dnsaasrecord'),
    ]

    operations = [
        migrations.RunPython(dnsaas_records_creation)
    ]
