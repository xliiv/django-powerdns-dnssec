# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import connection, migrations


def dnsaas_records_creation(apps, schema_editor):
    """
    Creates DNSaaSRecord for every Record.
    """
    with connection.cursor() as c:
        sql = """
        INSERT INTO powerdns_dnsaasrecord (record_ptr_id)
        SELECT id from records;
        """.strip()
        c.execute(sql)


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0025_auto_20160721_0517'),
    ]

    operations = [
        migrations.RunPython(
            dnsaas_records_creation,
            # no need for reverse
            reverse_code=lambda x, y: None
        )
    ]
