# Generated by Django 2.1.5 on 2019-02-01 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smartdevice', '0009_auto_20190201_0603'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smartdevice',
            name='functions',
            field=models.ManyToManyField(blank=True, default=None, to='smartdevice.SmartFunction'),
        ),
    ]