def getEmaList(df, span):
    df = df.ewm(span=span, adjust=False).mean()
    df = df.fillna(0)
    df[0:span] = None

    df = df.round(2)

    list = df.values.tolist()

    return list