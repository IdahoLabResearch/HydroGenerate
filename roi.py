# -*- coding: utf-8 -*-
"""
Created on Fri Oct  1 15:03:40 2021

@author: MITRB
"""

'''
Calculating the ROI % for a 5 year period
'''
'''
ROI: Return Of Investment is the (initial cost - final cost)/initial cost
'''

capex = [154800, 4850754, 5005554]
opex = [1710, 121268, 122978]

revenue_nma = [28793, 197500, 257656]
n = 5
for i in range(len(capex)):
    
    roi = (((capex[i] + n*opex[i])-(n*revenue_nma[i]))/(n*revenue_nma[i]))/100
    
    #payback = (2*capex[i])/(revenue_nma[i]-(2*opex[i]))
    print(roi)
    #print(payback)                                                   