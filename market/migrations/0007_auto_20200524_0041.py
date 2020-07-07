# Generated by Django 3.0.2 on 2020-05-23 22:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0006_stockexchange_country_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='D_analysis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset_datetime', models.CharField(db_index=True, max_length=64, unique=True)),
                ('d_tc_btlema17', models.CharField(max_length=32, null=True)),
                ('d_tc_btlema34', models.CharField(max_length=32, null=True)),
                ('d_tc_decpvpc', models.CharField(max_length=32, null=True)),
                ('d_tc_range', models.CharField(max_length=32, null=True)),
                ('d_tc_trend', models.CharField(max_length=32, null=True)),
                ('d_raw', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='market.D_raw')),
            ],
        ),
        migrations.AlterField(
            model_name='d_var',
            name='d_var_closepc305',
            field=models.FloatField(null=True, verbose_name='Percent variation between values'),
        ),
        migrations.AlterField(
            model_name='d_var',
            name='d_var_closepc72',
            field=models.FloatField(null=True, verbose_name='Percent variation between values'),
        ),
        migrations.AlterField(
            model_name='d_var',
            name='d_var_closepv305',
            field=models.FloatField(null=True, verbose_name='Percent variation between values'),
        ),
        migrations.AlterField(
            model_name='d_var',
            name='d_var_closepv72',
            field=models.FloatField(null=True, verbose_name='Percent variation between values'),
        ),
        migrations.AlterField(
            model_name='d_var',
            name='d_var_emaclose12922584',
            field=models.FloatField(null=True, verbose_name='Percent variation between values'),
        ),
        migrations.AlterField(
            model_name='d_var',
            name='d_var_emaclose144305',
            field=models.FloatField(null=True, verbose_name='Percent variation between values'),
        ),
        migrations.AlterField(
            model_name='d_var',
            name='d_var_emaclose1734',
            field=models.FloatField(null=True, verbose_name='Percent variation between values'),
        ),
        migrations.AlterField(
            model_name='d_var',
            name='d_var_emaclose305610',
            field=models.FloatField(null=True, verbose_name='Percent variation between values'),
        ),
        migrations.AlterField(
            model_name='d_var',
            name='d_var_emaclose3472',
            field=models.FloatField(null=True, verbose_name='Percent variation between values'),
        ),
        migrations.AlterField(
            model_name='d_var',
            name='d_var_emaclose6101292',
            field=models.FloatField(null=True, verbose_name='Percent variation between values'),
        ),
        migrations.AlterField(
            model_name='d_var',
            name='d_var_emaclose72144',
            field=models.FloatField(null=True, verbose_name='Percent variation between values'),
        ),
        migrations.AlterField(
            model_name='d_var',
            name='d_var_highpc305',
            field=models.FloatField(null=True, verbose_name='Percent variation between values'),
        ),
        migrations.AlterField(
            model_name='d_var',
            name='d_var_highpc72',
            field=models.FloatField(null=True, verbose_name='Percent variation between values'),
        ),
        migrations.AlterField(
            model_name='d_var',
            name='d_var_lowpv305',
            field=models.FloatField(null=True, verbose_name='Percent variation between values'),
        ),
        migrations.AlterField(
            model_name='d_var',
            name='d_var_lowpv72',
            field=models.FloatField(null=True, verbose_name='Percent variation between values'),
        ),
        migrations.DeleteModel(
            name='D_rating',
        ),
    ]
