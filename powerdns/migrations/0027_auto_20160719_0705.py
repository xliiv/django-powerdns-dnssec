# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0026_auto_20160719_0441'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dnsaasrecord',
            name='purpose',
            field=models.CharField(verbose_name='purpose', blank=True, null=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='recordrequest',
            name='record',
            field=models.ForeignKey(blank=True, to='powerdns.DNSaaSRecord', db_constraint=False, help_text='The record for which a change is being requested', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='requests'),
        ),
    ]
