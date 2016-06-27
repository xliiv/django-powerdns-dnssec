# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields.json


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0024_auto_20160623_0758'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deleterequest',
            name='last_change_json',
            field=django_extensions.db.fields.json.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='domainrequest',
            name='last_change_json',
            field=django_extensions.db.fields.json.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='recordrequest',
            name='last_change_json',
            field=django_extensions.db.fields.json.JSONField(blank=True, null=True),
        ),
    ]
