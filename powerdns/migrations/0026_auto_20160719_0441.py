# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def dnsaas_records_creation(apps, schema_editor):
    """
    Creates DNSaaSRecord for every Record.
    """
    #Person = apps.get_model("yourappname", "Person")
    raise Exception("TODO")


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0025_dnsaasrecord'),
    ]

    operations = [
        migrations.RunPython(dnsaas_records_creation)
    ]
