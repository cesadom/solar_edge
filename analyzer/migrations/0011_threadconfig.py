# Generated by Django 2.1.7 on 2019-02-22 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyzer', '0010_auto_20190119_2217'),
    ]

    operations = [
        migrations.CreateModel(
            name='ThreadConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('threadRun', models.IntegerField(blank=True, default=1, null=True)),
            ],
        ),
    ]
