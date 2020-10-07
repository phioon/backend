def getSmaList(df, span):
    df = df.rolling(span).mean()
    df = df.fillna(0)
    df[0:span] = None
    df = df.round(2)

    df = df.where(df.notnull(), None)

    result = df.values.tolist()
    return result
