# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0024_auto_20160627_0658'),
    ]

    operations = [
        migrations.CreateModel(
            name='DNSaaSRecord',
            fields=[
                ('record_ptr', models.OneToOneField(serialize=False, parent_link=True, auto_created=True, to='powerdns.Record', primary_key=True)),
                ('purpose', models.CharField(blank=True, max_length=255, null=True, verbose_name='purpose')),
            ],
            options={
                'verbose_name': 'Record',
            },
            bases=('powerdns.record',),
        ),
        migrations.AlterField(
            model_name='recordrequest',
            name='record',
            field=models.ForeignKey(to='powerdns.DNSaaSRecord', related_name='requests', blank=True, on_delete=django.db.models.deletion.DO_NOTHING, help_text='The record for which a change is being requested', null=True, db_constraint=False),
        ),
    ]
