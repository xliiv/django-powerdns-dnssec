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
            name='DomainOwner',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('ownership_type', models.CharField(choices=[('BO', 'Business Owner'), ('TO', 'Technical Owner')], max_length=10, db_index=True)),
                ('domain', models.ForeignKey(to='powerdns.Domain')),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='service',
            name='owners',
            field=models.ManyToManyField(related_name='service_owners', through='powerdns.ServiceOwner', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='domain',
            name='owners',
            field=models.ManyToManyField(related_name='domain_owners', through='powerdns.DomainOwner', to=settings.AUTH_USER_MODEL),
        ),
    ]
