# Generated by Django 3.0.2 on 2020-04-18 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0004_auto_20200303_0058'),
    ]

    operations = [
        migrations.AddField(
            model_name='stockexchange',
            name='currency_code',
            field=models.CharField(default='BRL', max_length=8, verbose_name='ISO 4217 Code'),
            preserve_default=False,
        ),
    ]
