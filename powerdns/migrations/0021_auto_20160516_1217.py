# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('powerdns', '0020_remove_recordrequest_target_ordername'),
    ]

    operations = [
        migrations.RenameField(
            model_name='deleterequest',
            old_name='owner',
            new_name='reporter',
        ),
        migrations.RenameField(
            model_name='domainrequest',
            old_name='target_account',
            new_name='account',
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
            old_name='target_record_auto_ptr',
            new_name='record_auto_ptr',
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
            old_name='target_ttl',
            new_name='ttl',
        ),
        migrations.RenameField(
            model_name='recordrequest',
            old_name='target_type',
            new_name='type',
        ),
        migrations.RemoveField(
            model_name='domainrequest',
            name='target_owner',
        ),
        migrations.RemoveField(
            model_name='recordrequest',
            name='target_owner',
        ),
        migrations.AddField(
            model_name='domainrequest',
            name='reporter',
            field=models.ForeignKey(blank=True, null=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recordrequest',
            name='reporter',
            field=models.ForeignKey(blank=True, null=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='domainrequest',
            name='owner',
            field=models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, verbose_name='Owner', related_name='+'),
        ),
        migrations.AlterField(
            model_name='recordrequest',
            name='owner',
            field=models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, verbose_name='Owner', related_name='+'),
        ),
    ]
