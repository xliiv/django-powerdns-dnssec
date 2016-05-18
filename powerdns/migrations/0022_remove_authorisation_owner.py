# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0021_auto_20160516_1217'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='authorisation',
            name='owner',
        ),
    ]
