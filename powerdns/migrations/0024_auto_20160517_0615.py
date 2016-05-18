# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import powerdns.utils
import dj.choices.fields


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0023_recordrequest_record_auto_ptr'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recordrequest',
            name='record_auto_ptr',
        ),
        migrations.AddField(
            model_name='recordrequest',
            name='auto_ptr',
            field=dj.choices.fields.ChoiceField(verbose_name='Auto PTR record', choices=powerdns.utils.AutoPtrOptions, default=2),
        ),
    ]
