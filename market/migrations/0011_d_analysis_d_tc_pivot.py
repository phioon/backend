# Generated by Django 3.0.2 on 2020-05-24 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0010_auto_20200524_0235'),
    ]

    operations = [
        migrations.AddField(
            model_name='d_analysis',
            name='d_tc_pivot',
            field=models.CharField(max_length=32, null=True),
        ),
    ]
