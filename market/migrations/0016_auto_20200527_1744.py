# Generated by Django 3.0.2 on 2020-05-27 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0015_auto_20200526_0953'),
    ]

    operations = [
        migrations.RenameField(
            model_name='d_analysis',
            old_name='tc_main',
            new_name='tc_setup',
        ),
        migrations.AddField(
            model_name='d_analysis',
            name='max_price',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='d_analysis',
            name='stop_loss',
            field=models.FloatField(null=True),
        ),
    ]
