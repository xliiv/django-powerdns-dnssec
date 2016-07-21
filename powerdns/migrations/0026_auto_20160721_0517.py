# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import connection, migrations


def dnsaas_records_creation(apps, schema_editor):
    """
    Creates DNSaaSRecord for every Record.
    """
    cursor = connection.cursor()
    SQL = """
    INSERT INTO powerdns_dnsaasrecord (record_ptr_id)
    SELECT id from records;
    """.strip()
    cursor.execute(SQL)


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0025_auto_20160721_0517'),
    ]

    operations = [
        migrations.RunPython(
            dnsaas_records_creation,
            #TODO:: reverse?
            reverse_code=lambda x, y: None
        )
    ]
