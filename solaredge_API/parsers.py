import pandas as pd


def parse_energydetails(d):
    def to_series(d):
        for meter in d['energyDetails']['meters']:
            name = meter['type']
            df = pd.DataFrame.from_dict(meter['values'])
            df = df.set_index('date')
            df.index = pd.DatetimeIndex(df.index)
            if df.empty:
                continue
            ts = df.value
            ts.name = name
            ts = ts.dropna()
            yield ts

    all_series = to_series(d)
    df = pd.concat(all_series, axis=1)
    return df
