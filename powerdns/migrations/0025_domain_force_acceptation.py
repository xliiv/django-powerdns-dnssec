# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0024_auto_20160517_0615'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='force_acceptation',
            field=models.BooleanField(verbose_name='Force accept', default=False, help_text='if checked Records related to this domain will be immediately accepted'),
        ),
    ]
