# Generated by Django 3.1.7 on 2021-03-12 08:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0022_auto_20210312_0737'),
    ]

    operations = [
        migrations.RenameField(
            model_name='d_tc',
            old_name='phibo_alignment',
            new_name='pvpc_alignment',
        ),
        migrations.RenameField(
            model_name='d_tc',
            old_name='phibo_test',
            new_name='pvpc_test',
        ),
    ]
