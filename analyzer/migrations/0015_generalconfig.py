# Generated by Django 2.1.7 on 2019-03-01 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyzer', '0014_solarmeasurement_power_powergrid'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneralConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('generalConfigGroup', models.CharField(max_length=20)),
                ('generalConfigKey', models.CharField(max_length=150)),
                ('generalValue', models.CharField(max_length=150)),
            ],
        ),
    ]
