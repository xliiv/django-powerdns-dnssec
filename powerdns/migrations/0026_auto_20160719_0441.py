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

        #Record = apps.get_model('powerdns', 'Record')
        DNSaaSRecord = apps.get_model('powerdns', 'DNSaaSRecord')

        print()
        print(apps.get_model('powerdns', 'Record').objects.count())
        print(apps.get_model('powerdns', 'DNSaaSRecord').objects.count())

        dnsaas_record = DNSaaSRecord(record_ptr_id=record.pk)
        data = record.__dict__
        del data['id']
        dnsaas_record.__dict__.update(data)
        dnsaas_record.save()

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
