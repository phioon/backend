def getRocList(df, span):
    df = df.pct_change(periods=span)
    df = df.fillna(0)
    df[0:span*2] = None

    df = df.round(4)

    list = df.values.tolist()

    return list