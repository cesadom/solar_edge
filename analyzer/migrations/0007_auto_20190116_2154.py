# Generated by Django 2.1.5 on 2019-01-16 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyzer', '0006_auto_20190116_2152'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='description',
            field=models.TextField(),
        ),
    ]
