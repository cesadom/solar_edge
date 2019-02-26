# Generated by Django 2.1.7 on 2019-02-22 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyzer', '0011_threadconfig'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='threadconfig',
            name='threadRun',
        ),
        migrations.AddField(
            model_name='threadconfig',
            name='threadConfig',
            field=models.CharField(default=1, max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='threadconfig',
            name='threadValue',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
    ]