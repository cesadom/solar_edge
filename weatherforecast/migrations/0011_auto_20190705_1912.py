# Generated by Django 2.2.3 on 2019-07-05 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weatherforecast', '0010_auto_20190301_1554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weatherforecast',
            name='forecastDate',
            field=models.DateField(default='2019-07-05'),
        ),
    ]
