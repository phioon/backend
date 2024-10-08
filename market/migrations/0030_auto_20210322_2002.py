# Generated by Django 3.1.7 on 2021-03-22 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0029_auto_20210321_0809'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stockexchange',
            old_name='se_endTime',
            new_name='end_time',
        ),
        migrations.RenameField(
            model_name='stockexchange',
            old_name='se_startTime',
            new_name='start_time',
        ),
        migrations.RenameField(
            model_name='stockexchange',
            old_name='se_timezone',
            new_name='timezone',
        ),
        migrations.AlterField(
            model_name='stockexchange',
            name='se_short',
            field=models.CharField(max_length=32, primary_key=True, serialize=False, verbose_name='Stock Exchange Symbol'),
        ),
    ]
