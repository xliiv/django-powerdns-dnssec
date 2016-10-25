# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('powerdns', '0029_auto_20160922_0757'),
    ]

    operations = [
        migrations.CreateModel(
            name='DomainOwnership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('ownership_type', models.CharField(max_length=10, choices=[('BO', 'Business Owner'), ('TO', 'Technical Owner')], db_index=True)),
                ('domain', models.ForeignKey(to='powerdns.Domain')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
