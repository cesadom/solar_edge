# Generated by Django 2.1.7 on 2019-02-22 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weatherforecast', '0006_auto_20190201_0541'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weatherforecast',
            name='forecastDate',
            field=models.DateField(default='2019-02-22'),
        ),
    ]
