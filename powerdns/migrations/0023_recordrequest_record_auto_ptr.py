# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import dj.choices.fields
import powerdns.utils


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0022_remove_authorisation_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='recordrequest',
            name='record_auto_ptr',
            field=dj.choices.fields.ChoiceField(help_text='Should A records have auto PTR by default', choices=powerdns.utils.AutoPtrOptions, default=2),
        ),
    ]
