# Generated by Django 3.0.2 on 2020-05-25 20:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0013_auto_20200524_2110'),
    ]

    operations = [
        migrations.RenameField(
            model_name='d_analysis',
            old_name='d_tc_btlema',
            new_name='tc_btlema',
        ),
        migrations.RenameField(
            model_name='d_analysis',
            old_name='d_tc_pivot',
            new_name='tc_pivot',
        ),
        migrations.RenameField(
            model_name='d_analysis',
            old_name='d_tc_pvpc',
            new_name='tc_pvpc',
        ),
        migrations.RenameField(
            model_name='d_analysis',
            old_name='d_tc_trend',
            new_name='tc_trend',
        ),
    ]
