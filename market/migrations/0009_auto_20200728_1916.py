# Generated by Django 3.0.8 on 2020-07-28 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0008_remove_asset_asset_volatility'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logging',
            name='message',
            field=models.TextField(),
        ),
    ]
