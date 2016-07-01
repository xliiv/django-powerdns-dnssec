# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0023_domaintemplate_is_public_domain'),
    ]

    operations = [
        migrations.RenameField(
            model_name='domain',
            old_name='record_auto_ptr',
            new_name='auto_ptr',
        ),
        migrations.RenameField(
            model_name='domainrequest',
            old_name='target_record_auto_ptr',
            new_name='target_auto_ptr',
        ),
        migrations.RenameField(
            model_name='domaintemplate',
            old_name='record_auto_ptr',
            new_name='auto_ptr',
        ),
    ]
