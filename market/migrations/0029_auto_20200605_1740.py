# Generated by Django 3.0.2 on 2020-06-05 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0028_auto_20200605_1548'),
    ]

    operations = [
        migrations.RenameField(
            model_name='d_analysis',
            old_name='tc_btlema',
            new_name='ema_btl',
        ),
        migrations.RenameField(
            model_name='d_analysis',
            old_name='tc_decpvpc',
            new_name='btl_emaroc',
        ),
        migrations.RenameField(
            model_name='d_analysis',
            old_name='tc_pivot',
            new_name='pivot',
        ),
        migrations.RenameField(
            model_name='d_analysis',
            old_name='tc_trend',
            new_name='phibo_test',
        ),
        migrations.AddField(
            model_name='d_analysis',
            name='ema_trend',
            field=models.CharField(max_length=32, null=True),
        ),
    ]
