# Generated by Django 2.1.5 on 2019-02-01 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smartdevice', '0005_smartdevice_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smartdevice',
            name='functions',
            field=models.ManyToManyField(blank=True, default=None, null=True, to='smartdevice.SmartFunction'),
        ),
    ]
