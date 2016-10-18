# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('powerdns', '0029_auto_20160922_0757'),
    ]

    operations = [
        migrations.CreateModel(
            name='DomainAcceptance',
            fields=[
                ('domain', models.OneToOneField(to='powerdns.Domain', related_name='acceptance', serialize=False, primary_key=True)),
                ('require_sec_acceptance', models.BooleanField(default=False, help_text='Do new A records require security acceptance')),
                ('require_seo_acceptance', models.BooleanField(default=False, help_text='Does deleting A records require SEO acceptance')),
            ],
        ),
    ]
