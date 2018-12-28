# Generated by Django 2.1.3 on 2018-12-28 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyzer', '0003_auto_20181225_2233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solarmeasurement',
            name='energyConsumtion',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='solarmeasurement',
            name='energyProduction',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
    ]
