import pandas as pd


class RawData:
    stock_exchange = None
    asset = None
    asset_symbol = None
    last_periods = 10

    ema_periods = [8, 9, 17, 34, 50, 72, 144, 200, 305, 610, 1292, 2584]
    sma_periods = [7, 10, 20, 21, 30, 50, 55, 100, 200]

    tc_min_periods = 72

    cache = {
        'raw': {'qs': [], 'df': pd.DataFrame()},
        'pvpc': {'df': pd.DataFrame()},
        'ema': {'df': pd.DataFrame()},
        'sma': {'df': pd.DataFrame()},
        'var': {'df': pd.DataFrame()},
        'tc': {'df': pd.DataFrame()},
    }
