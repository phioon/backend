# Generated by Django 3.1.7 on 2021-03-21 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0028_auto_20210320_1909'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='d_phioperation',
            name='unique_asset_tc',
        ),
        migrations.RenameField(
            model_name='d_phistats',
            old_name='asset_symbol',
            new_name='asset',
        ),
        migrations.RenameField(
            model_name='d_phistats',
            old_name='has_position_open',
            new_name='has_open_position',
        ),
        migrations.RemoveField(
            model_name='d_phistats',
            name='asset_setup',
        ),
        migrations.AddField(
            model_name='d_phistats',
            name='canceled_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='d_phioperation',
            name='entry_price',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='d_phioperation',
            name='gain_percent',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='d_phioperation',
            name='loss_percent',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='d_phioperation',
            name='risk_reward',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='d_phioperation',
            name='stop_loss',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='d_phioperation',
            name='target',
            field=models.JSONField(default=dict),
        ),
        migrations.AddConstraint(
            model_name='d_phioperation',
            constraint=models.UniqueConstraint(fields=('asset', 'tc', 'radar_on'), name='unique_asset_tc_date'),
        ),
        migrations.AddConstraint(
            model_name='d_phistats',
            constraint=models.UniqueConstraint(fields=('asset', 'tc'), name='unique_asset_tc'),
        ),
    ]
