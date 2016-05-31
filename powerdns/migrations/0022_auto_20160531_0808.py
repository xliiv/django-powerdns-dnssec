# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0021_tsigkeys'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recordrequest',
            name='record',
            field=models.ForeignKey(related_name='requests', to='powerdns.Record', db_constraint=False, help_text='The record for which a change is being requested', null=True, on_delete=django.db.models.deletion.DO_NOTHING, blank=True),
        ),
    ]
