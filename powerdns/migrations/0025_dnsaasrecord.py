# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0024_auto_20160627_0658'),
    ]

    operations = [
        migrations.CreateModel(
            name='DNSaaSRecord',
            fields=[
                ('record_ptr', models.OneToOneField(auto_created=True, to='powerdns.Record', serialize=False, parent_link=True, primary_key=True)),
                ('purpose', models.CharField(verbose_name='purpose', max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('powerdns.record',),
        ),
    ]
