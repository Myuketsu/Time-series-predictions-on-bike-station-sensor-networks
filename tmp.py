import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from mycolorpy import colorlist as mcp

DATE_RANGE = ('04-01-2016', '10-31-2016')

df = pd.read_csv(
    f'./data/city/Toulouse/X_hour_toulouse.csv',
    index_col=0
)
df['date'] = pd.date_range(*DATE_RANGE, freq='1h')[:len(df)]

df.set_index('date', inplace=True)
df_mean_by_hour = df.groupby(df.index.hour).mean()

from data.data import get_acp_dataframe, get_tsne_dataframe
get_acp_dataframe(df_mean_by_hour.T)

# get_tsne_dataframe(df)