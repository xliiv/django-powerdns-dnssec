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
            field=models.ForeignKey(related_name='requests', null=True, db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, help_text='The record for which a change is being requested', blank=True, to='powerdns.Record'),
        ),
        migrations.AlterField(
            model_name='tsigkeys',
            name='name',
            field=models.CharField(max_length=255, verbose_name='name', help_text='Key name'),
        ),
        migrations.AlterField(
            model_name='tsigkeys',
            name='secret',
            field=models.CharField(max_length=255, verbose_name='secret', help_text='Secret key'),
        ),
    ]
