# Generated by Django 3.1.7 on 2021-04-21 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0038_auto_20210417_0725'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='d_phioperation',
            name='d_phioperation__asset_tc_date',
        ),
        migrations.AddConstraint(
            model_name='d_phioperation',
            constraint=models.UniqueConstraint(fields=('asset', 'radar_on'), name='d_phioperation__asset_datetime'),
        ),
    ]
