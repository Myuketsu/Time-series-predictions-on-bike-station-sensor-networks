import pandas as pd

def predict_by_mean(df: pd.DataFrame):
    df = df.copy()
    df['days'] = df.index.day_name()
    df['hours'] = df.index.hour
    df['days'] = pd.Categorical(df['days'], categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], ordered=True)

    return df.groupby(['days', 'hours']).mean()
    
