import pandas as pd
import numpy as np

df = pd.read_csv('./data/city/Toulouse/X_hour_toulouse.csv', index_col=0)
df['date'] = pd.date_range('04-01-2016', '10-31-2016', freq='1h')[:len(df)]
a = df.columns.str.split('-', n=1, expand=True).get_level_values(1)

r = []
l = ['a', 'b', 'c']
r = np.array([[[i, y] for i in a] for y in a])
print(np.array(r))