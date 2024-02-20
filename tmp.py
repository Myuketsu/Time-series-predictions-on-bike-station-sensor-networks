import pandas as pd

df = pd.read_csv('./data/city/Toulouse/X_hour_toulouse.csv', index_col=0)
df['date'] = pd.date_range('04-01-2016', '10-31-2016', freq='1h')[:len(df)]
print(df['date'].min().date())