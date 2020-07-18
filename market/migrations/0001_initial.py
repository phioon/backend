# Generated by Django 3.0.8 on 2020-07-17 23:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('created_time', models.DateField(auto_now_add=True)),
                ('modified_time', models.DateField(auto_now=True)),
                ('last_access_time', models.DateField(db_index=True, default='2001-01-01')),
                ('asset_symbol', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('asset_label', models.CharField(max_length=32)),
                ('asset_name', models.CharField(max_length=128)),
                ('asset_lastTradeTime', models.CharField(max_length=32, null=True)),
                ('asset_price', models.FloatField(null=True)),
                ('asset_pct_change', models.FloatField(null=True)),
                ('asset_volatility', models.FloatField(null=True, verbose_name='Volatility percentage over last 10 days.')),
                ('asset_volume_avg', models.IntegerField(null=True, verbose_name='Volume average over last 10 days.')),
                ('is_considered', models.BooleanField(default=False, verbose_name='Is it considered in the entire App/frontend?')),
                ('is_considered_for_analysis', models.BooleanField(default=False, verbose_name='Is it considered in Setup classes?')),
            ],
        ),
        migrations.CreateModel(
            name='D_raw',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset_datetime', models.CharField(db_index=True, max_length=64, unique=True)),
                ('d_datetime', models.CharField(db_index=True, max_length=32)),
                ('d_open', models.FloatField()),
                ('d_high', models.FloatField()),
                ('d_low', models.FloatField()),
                ('d_close', models.FloatField()),
                ('d_volume', models.BigIntegerField()),
                ('asset_symbol', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='market.Asset', verbose_name='Asset Symbol')),
            ],
        ),
        migrations.CreateModel(
            name='Logging',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log_datetime', models.DateTimeField(auto_now=True)),
                ('log_level', models.CharField(max_length=8)),
                ('log_module', models.CharField(max_length=64)),
                ('log_message', models.TextField(max_length=2048)),
                ('log_created_by', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='StockExchange',
            fields=[
                ('se_createdTime', models.DateField(auto_now_add=True)),
                ('se_short', models.CharField(max_length=32, primary_key=True, serialize=False, verbose_name='Stock Exchange Short')),
                ('se_name', models.CharField(db_index=True, max_length=128, verbose_name='Stock Exchange Name')),
                ('se_startTime', models.TimeField(default='10:00:00', verbose_name='Usual time the market starts')),
                ('se_endTime', models.TimeField(default='18:00:00', verbose_name='Usual time the market ends')),
                ('se_timezone', models.CharField(max_length=32, verbose_name='Timezone (TZ database name)')),
                ('country_code', models.CharField(max_length=8, verbose_name='Alpha-2 Code')),
                ('currency_code', models.CharField(max_length=8, verbose_name='ISO 4217 Code')),
                ('provider_realtime', models.CharField(default='AV', max_length=8)),
                ('provider_timeseries', models.CharField(default='AV', max_length=8)),
            ],
        ),
        migrations.CreateModel(
            name='TechnicalCondition',
            fields=[
                ('id', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('type', models.CharField(max_length=12)),
                ('description', models.TextField(max_length=2048)),
                ('score', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='D_var',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset_datetime', models.CharField(db_index=True, max_length=64, unique=True)),
                ('d_var_emaclose1734', models.FloatField(null=True, verbose_name='Percent variation between values')),
                ('d_var_emaclose3472', models.FloatField(null=True, verbose_name='Percent variation between values')),
                ('d_var_emaclose72144', models.FloatField(null=True, verbose_name='Percent variation between values')),
                ('d_var_emaclose144305', models.FloatField(null=True, verbose_name='Percent variation between values')),
                ('d_var_emaclose305610', models.FloatField(null=True, verbose_name='Percent variation between values')),
                ('d_raw', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='market.D_raw', verbose_name='Asset and Datetime')),
            ],
        ),
        migrations.CreateModel(
            name='D_technicalCondition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset_datetime', models.CharField(db_index=True, max_length=64, unique=True)),
                ('pivot', models.IntegerField(null=True)),
                ('low_ema_btl', models.IntegerField(null=True)),
                ('high_ema_btl', models.IntegerField(null=True)),
                ('emaroc_btl', models.IntegerField(null=True)),
                ('ema_range', models.IntegerField(null=True)),
                ('ema_trend', models.IntegerField(null=True)),
                ('ema_test', models.IntegerField(null=True)),
                ('phibo_alignment', models.IntegerField(null=True)),
                ('phibo_test', models.IntegerField(null=True)),
                ('d_raw', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='market.D_raw')),
            ],
        ),
        migrations.CreateModel(
            name='D_setupSummary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset_setup', models.CharField(db_index=True, max_length=64, unique=True)),
                ('has_position_open', models.BooleanField(default=False)),
                ('occurrencies', models.IntegerField(default=0)),
                ('gain_count', models.IntegerField(default=0)),
                ('loss_count', models.IntegerField(default=0)),
                ('success_rate', models.FloatField(default=0)),
                ('avg_duration_gain', models.IntegerField(null=True)),
                ('avg_duration_loss', models.IntegerField(null=True)),
                ('last_ended_occurrence', models.CharField(max_length=32, null=True)),
                ('last_ended_duration', models.IntegerField(null=True)),
                ('last_was_success', models.BooleanField(null=True)),
                ('asset_symbol', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='market.Asset')),
                ('tc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='market.TechnicalCondition')),
            ],
        ),
        migrations.CreateModel(
            name='D_setup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset_datetime', models.CharField(db_index=True, max_length=64, unique=True)),
                ('asset_setup', models.CharField(db_index=True, max_length=64)),
                ('started_on', models.CharField(max_length=32, null=True)),
                ('ended_on', models.CharField(max_length=32, null=True)),
                ('is_success', models.BooleanField(null=True)),
                ('duration', models.IntegerField(default=True)),
                ('max_price', models.FloatField(null=True)),
                ('target', models.FloatField(null=True)),
                ('stop_loss', models.FloatField(null=True)),
                ('gain_percent', models.FloatField(null=True)),
                ('loss_percent', models.FloatField(null=True)),
                ('risk_reward', models.FloatField(null=True)),
                ('fibo_periods_needed', models.FloatField(null=True)),
                ('fibo_p1', models.FloatField(null=True)),
                ('fibo_p2', models.FloatField(null=True)),
                ('fibo_p3', models.FloatField(null=True)),
                ('fibo_wave_1', models.FloatField(null=True)),
                ('fibo_retraction', models.FloatField(null=True)),
                ('fibo_pct_retraction', models.FloatField(null=True)),
                ('fibo_projection', models.FloatField(null=True)),
                ('d_raw', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='market.D_raw')),
                ('tc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='market.TechnicalCondition')),
            ],
        ),
        migrations.CreateModel(
            name='D_roc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset_datetime', models.CharField(db_index=True, max_length=64, unique=True)),
                ('d_roc_close2', models.FloatField(null=True)),
                ('d_roc_close3', models.FloatField(null=True)),
                ('d_roc_high2', models.FloatField(null=True)),
                ('d_roc_low2', models.FloatField(null=True)),
                ('d_roc_emaclose17', models.FloatField(null=True)),
                ('d_roc_emaclose34', models.FloatField(null=True)),
                ('d_roc_emaclose72', models.FloatField(null=True)),
                ('d_roc_emaclose144', models.FloatField(null=True)),
                ('d_roc_emaclose305', models.FloatField(null=True)),
                ('d_roc_emaclose610', models.FloatField(null=True)),
                ('d_roc_emaclose1292', models.FloatField(null=True)),
                ('d_roc_emaclose2584', models.FloatField(null=True)),
                ('d_raw', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='market.D_raw', verbose_name='Asset and Datetime')),
            ],
        ),
        migrations.CreateModel(
            name='D_pvpc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset_datetime', models.CharField(db_index=True, max_length=64, unique=True)),
                ('d_pv72', models.FloatField(null=True)),
                ('d_pv305', models.FloatField(null=True)),
                ('d_pv1292', models.FloatField(null=True)),
                ('d_pc72', models.FloatField(null=True)),
                ('d_pc305', models.FloatField(null=True)),
                ('d_pc1292', models.FloatField(null=True)),
                ('d_raw', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='market.D_raw')),
            ],
        ),
        migrations.CreateModel(
            name='D_ema',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset_datetime', models.CharField(db_index=True, max_length=64, unique=True)),
                ('d_ema_close17', models.FloatField(null=True)),
                ('d_ema_close34', models.FloatField(null=True)),
                ('d_ema_close72', models.FloatField(null=True)),
                ('d_ema_close144', models.FloatField(null=True)),
                ('d_ema_close305', models.FloatField(null=True)),
                ('d_ema_close610', models.FloatField(null=True)),
                ('d_ema_close1292', models.FloatField(null=True)),
                ('d_ema_close2584', models.FloatField(null=True)),
                ('d_raw', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='market.D_raw')),
            ],
        ),
        migrations.AddField(
            model_name='asset',
            name='stockExchange',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assets', to='market.StockExchange'),
        ),
    ]
