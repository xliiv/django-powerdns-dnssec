# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0031_auto_20161028_0324'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recordrequest',
            old_name='service',
            new_name='target_service',
        ),
        migrations.RemoveField(
            model_name='domainrequest',
            name='service',
        ),
    ]
