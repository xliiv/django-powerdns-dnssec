# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0030_auto_20161026_0813'),
    ]

    operations = [
        migrations.RenameField(
            model_name='serviceowner',
            old_name='user',
            new_name='owner',
        ),
    ]
