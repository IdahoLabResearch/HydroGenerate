# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 17:09:42 2021

@author: MITRB
"""

import matplotlib.pyplot as plt
import numpy as np
# plt.close('all')

# # generate sample axis
# n = np.arange(0, 8760)
# l = np.size(n)
# imp = np.zeros(l)
# ind = np.where(n==0)
# imp[ind] = 1
# plt.subplot(2,1,1)
# plt.stem(n,imp); plt.title('Impulse Signal')
# plt.xlabel('Sample'); plt.ylabel('Amplitude')
# plt.grid(True)


def ramp(t,m,shift):
    r = np.zeros(N)
    for i in range(1,N):
        if shift >= -shift:
            r[i]=m*(t[i]+shift)/1944
    return r
t = np.linspace(0,1944,1944)
N = len(t)

shift = 0
r= ramp(t,1,0)
plt.plot(t,r)
plt.grid()
