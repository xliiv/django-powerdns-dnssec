# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0031_auto_20161026_0933'),
    ]

    operations = [
        migrations.RenameField(
            model_name='domain',
            old_name='owners',
            new_name='direct_owners',
        ),
    ]
