# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-29 12:02
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_prices_openexchangerates', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversionrate',
            name='rate',
            field=models.DecimalField(decimal_places=6, max_digits=13, verbose_name='Conversion rate'),
        ),
    ]
