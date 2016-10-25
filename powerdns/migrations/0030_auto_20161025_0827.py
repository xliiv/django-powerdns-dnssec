# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0029_auto_20160922_0757'),
    ]

    operations = [
        migrations.AddField(
            model_name='domain',
            name='require_sec_acceptance',
            field=models.BooleanField(default=False, help_text='Do new A records require security acceptance'),
        ),
        migrations.AddField(
            model_name='domain',
            name='require_seo_acceptance',
            field=models.BooleanField(default=False, help_text='Does deleting A records require SEO acceptance'),
        ),
    ]
