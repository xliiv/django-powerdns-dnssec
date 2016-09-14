# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('powerdns', '0026_auto_20160829_0337'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('name', models.CharField(verbose_name='name', unique=True, max_length=255)),
                ('uid', models.CharField(db_index=True, unique=True, max_length=100)),
                ('status', models.CharField(choices=[('ACTIVE', 'Active')], db_index=True, max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ServiceOwner',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('created', models.DateTimeField(verbose_name='date created', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='last modified', auto_now=True)),
                ('ownership_type', models.CharField(choices=[('BO', 'Business Owner'), ('TO', 'Technical Owner')], db_index=True, max_length=10)),
                ('service', models.ForeignKey(to='powerdns.Service')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='service',
            name='owners',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='powerdns.ServiceOwner'),
        ),
    ]
