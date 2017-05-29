# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0035_auto_20161228_0058'),
    ]

    operations = [
        migrations.RenameField(
            model_name='domainrequest',
            old_name='target_account',
            new_name='account',
        ),
        migrations.RenameField(
            model_name='domainrequest',
            old_name='target_auto_ptr',
            new_name='auto_ptr',
        ),
        migrations.RenameField(
            model_name='domainrequest',
            old_name='target_master',
            new_name='master',
        ),
        migrations.RenameField(
            model_name='domainrequest',
            old_name='target_name',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='domainrequest',
            old_name='target_remarks',
            new_name='remarks',
        ),
        migrations.RenameField(
            model_name='domainrequest',
            old_name='target_reverse_template',
            new_name='reverse_template',
        ),
        migrations.RenameField(
            model_name='domainrequest',
            old_name='target_service',
            new_name='service',
        ),
        migrations.RenameField(
            model_name='domainrequest',
            old_name='target_template',
            new_name='template',
        ),
        migrations.RenameField(
            model_name='domainrequest',
            old_name='target_type',
            new_name='type',
        ),
        migrations.RenameField(
            model_name='domainrequest',
            old_name='target_unrestricted',
            new_name='unrestricted',
        ),
        migrations.RenameField(
            model_name='recordrequest',
            old_name='target_auth',
            new_name='auth',
        ),
        migrations.RenameField(
            model_name='recordrequest',
            old_name='target_content',
            new_name='content',
        ),
        migrations.RenameField(
            model_name='recordrequest',
            old_name='target_disabled',
            new_name='disabled',
        ),
        migrations.RenameField(
            model_name='recordrequest',
            old_name='target_name',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='recordrequest',
            old_name='target_prio',
            new_name='prio',
        ),
        migrations.RenameField(
            model_name='recordrequest',
            old_name='target_remarks',
            new_name='remarks',
        ),
        migrations.RenameField(
            model_name='recordrequest',
            old_name='target_service',
            new_name='service',
        ),
        migrations.RenameField(
            model_name='recordrequest',
            old_name='target_ttl',
            new_name='ttl',
        ),
        migrations.RenameField(
            model_name='recordrequest',
            old_name='target_type',
            new_name='type',
        ),
    ]
