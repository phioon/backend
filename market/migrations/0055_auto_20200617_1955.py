# Generated by Django 3.0.2 on 2020-06-17 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0054_d_setup_fibo_periods_needed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='d_setupsummary',
            name='last_ended_occurrence',
            field=models.CharField(max_length=32, null=True),
        ),
    ]
