# Generated by Django 3.1.7 on 2021-03-19 18:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0025_auto_20210313_2023'),
    ]

    operations = [
        migrations.AlterField(
            model_name='d_phioperation',
            name='asset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phi_operations', to='market.asset'),
        ),
        migrations.RemoveField(
            model_name='d_phioperation',
            name='entry_price',
        ),
        migrations.AddField(
            model_name='d_phioperation',
            name='entry_price',
            field=models.JSONField(default=list),
        ),
        migrations.RemoveField(
            model_name='d_phioperation',
            name='gain_percent',
        ),
        migrations.AddField(
            model_name='d_phioperation',
            name='gain_percent',
            field=models.JSONField(default=list),
        ),
        migrations.RemoveField(
            model_name='d_phioperation',
            name='loss_percent',
        ),
        migrations.AddField(
            model_name='d_phioperation',
            name='loss_percent',
            field=models.JSONField(default=list),
        ),
        migrations.RemoveField(
            model_name='d_phioperation',
            name='risk_reward',
        ),
        migrations.AddField(
            model_name='d_phioperation',
            name='risk_reward',
            field=models.JSONField(default=list),
        ),
        migrations.RemoveField(
            model_name='d_phioperation',
            name='stop_loss',
        ),
        migrations.AddField(
            model_name='d_phioperation',
            name='stop_loss',
            field=models.JSONField(default=list),
        ),
        migrations.RemoveField(
            model_name='d_phioperation',
            name='target',
        ),
        migrations.AddField(
            model_name='d_phioperation',
            name='target',
            field=models.JSONField(default=list),
        ),
        migrations.AlterField(
            model_name='d_phioperation',
            name='tc',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='phi_operations', to='market.technicalcondition'),
        ),
    ]
