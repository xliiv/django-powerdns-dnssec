# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0025_domain_force_acceptation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='domain',
            name='force_acceptation',
        ),
    ]
