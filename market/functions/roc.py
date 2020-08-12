import numpy as np


def getRocList(df, span):
    df = df.where(df.notnull(), np.nan)
    df = df.pct_change(periods=span)
    df[0:span*2] = None

    df = df.fillna(0)
    df = df.round(4)
    df = df.where(df.notnull(), None)

    result = df.values.tolist()
    return result
