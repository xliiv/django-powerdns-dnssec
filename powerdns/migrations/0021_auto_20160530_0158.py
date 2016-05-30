# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0020_remove_recordrequest_target_ordername'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recordrequest',
            name='record',
            field=models.ForeignKey(null=True, related_name='requests', on_delete=django.db.models.deletion.DO_NOTHING, blank=True, help_text='The record for which a change is being requested', db_constraint=False, to='powerdns.Record'),
        ),
    ]
