# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0032_auto_20161102_0626'),
    ]

    operations = [
        migrations.AddField(
            model_name='domainrequest',
            name='target_service',
            field=models.ForeignKey(to='powerdns.Service', blank=True, null=True),
        ),
    ]
