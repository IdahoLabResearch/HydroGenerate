# -*- coding: utf-8 -*-
"""
Created on Tue Jul 20 11:41:58 2021

@author: MITRB
"""

import pandas as pd
import numpy as np

df = pd.read_excel(r'C:\Work\Smart VGI\Data\CAISO_9am.xlsx')

val = df['Scaled'].values

new_val = np.repeat(val,300)

np.savetxt('C:\Work\My_Code\Files\caiso_test_HIL_CAISO_9am.txt',new_val)