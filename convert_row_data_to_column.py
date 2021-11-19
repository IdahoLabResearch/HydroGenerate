# -*- coding: utf-8 -*-
"""
Created on Mon Sep 20 09:20:03 2021

@author: MITRB
"""

import pandas as pd

df_lmp = pd.read_excel(r'C:\Work\My_Code\Files\LMP_DAM_ANTLER_6_N001.xlsx',sheet_name='2020')
new_idx = pd.date_range("2020-01-01", periods=8784, freq="H")

df_lmp_hourly = []

for idx, row in df_lmp.iterrows():
    row_t = row.transpose()
    df_lmp_hourly.append(pd.DataFrame(data={'lmp':row_t[1:25].values}))

df_lmp_hourly = pd.concat(df_lmp_hourly)
df_lmp_hourly['dateTime'] = new_idx
df_lmp_hourly.set_index('dateTime',inplace=True)
df_lmp_hourly.to_csv(r'C:\Work\My_Code\Files\LMP_2020.csv')