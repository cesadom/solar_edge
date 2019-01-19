# Generated by Django 2.1.5 on 2019-01-19 21:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('weatherforecast', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeatherForecast',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(max_length=10)),
                ('sunHours', models.DecimalField(decimal_places=1, max_digits=3)),
            ],
        ),
        migrations.CreateModel(
            name='WeatherForecastDayHour',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('chanceofsunshine', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('weatherForecast', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='weatherforecast.WeatherForecast')),
            ],
        ),
        migrations.RemoveField(
            model_name='smartdevice',
            name='functions',
        ),
        migrations.DeleteModel(
            name='SmartDevice',
        ),
        migrations.DeleteModel(
            name='SmartFunction',
        ),
    ]
