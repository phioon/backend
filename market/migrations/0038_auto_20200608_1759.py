# Generated by Django 3.0.2 on 2020-06-08 15:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0037_auto_20200608_1720'),
    ]

    operations = [
        migrations.AlterField(
            model_name='d_setup',
            name='tc',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='market.TechnicalCondition'),
        ),
    ]
