# Generated by Django 3.0.8 on 2020-07-07 17:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0059_auto_20200703_1903'),
    ]

    operations = [
        migrations.RenameField(
            model_name='asset',
            old_name='asset_is_exception',
            new_name='asset_is_ignorable',
        ),
    ]
