# -*- coding: utf-8 -*-
"""
Created on Sun Aug 16 14:15:46 2020

@author: MITRB
"""

from tkinter import *
import tkinter as ttk
from tkinter.ttk import *
import pywt
import numpy as np
import math
import pandas as pd
from tkinter import messagebox
#from john_code_VRG import diff_m, length, temp_input, angle
import matplotlib.pyplot as plt
from datetime import datetime
import sympy as sp
sp.init_printing()






#Declaring some constants

g = 9.81
rho = 1000

'''
1 ft = 0.3048m # Ft to m conversion
'''




'''
This maintains the turbine selection data based on head

Head suggesting the types of turbines to be used.
https://theconstructor.org/practical-guide/hydraulics-lab/turbines-pumps/factors-affecting-selection-hydraulic-turbine/30826/
'''

def turbine():
    turb_data = {'Head':['Very low head','Low head','Medium head','High head',
                         'Very high head','Very high head'],
                 'Start':[0.5,10,60,150,350,2000],
                 'End':[10,60,150,350,2000,5000],
                 'Turbine':['Kaplan turbine','Kaplan turbine',
                                     'Francis turbine','Francis turbine',
                                     'Pelton turbine','Pelton turbine'],
                 'k2':[800,800,600,600,0,0]}
    df = pd.DataFrame(data=turb_data)
    return df

def time_diff_hr(dt1,dt2):
    timedel = dt2 - dt1
    time_step_hr = (timedel.days*24*3600 + timedel.seconds)/3600
    return time_step_hr

#Converting the dictionary to DataFrame


def calculate_potential(flow_info, rated_flow=None, rated_power=None, turb= None, 
                        head_input=None,op='Timeseries', sys_effi=None,
                        system='pipe', energy_cost=None, cost = None, 
                        flow_column='Flow (cfs)'):
    
    df = turbine()

    diff_m = head_input* 0.3048 # converting ft. to m
    head=abs(diff_m)
    #length = length*1609.34 #Converting mi to m
    
    if head <= 0.6:
        #raise ValueError('Head height too low for small-scale hydropower')
        message="Head height too low for small-scale hydropower"
        # Ref: https://www.energy.gov/energysaver/planning-microhydropower-system
        
        raise SystemExit
        #dia = dia * 25.4 # converting inches to mm


    if (op == 'Timeseries'):
        flow_info[flow_column]=flow_info[flow_column].replace(['Ice','Mtn','Bkw','NaN','--','Dis','Dry',
                                                                       '***','Eqp','Rat','ZFI','Ssn','missing'],0)
        
        flow_info = flow_info.dropna(subset=[flow_column])
         
        if rated_flow is not None:
            maxflow = 0.028316846591999675*rated_flow
        else:
            maxflow = 0.028316846591999675*max(flow_info[flow_column])
        
        '''
        1 cu.ft/sec = 0.028316846591999675 cu.m/sec
        '''
        
        flow_range = flow_info[flow_column] * (0.028316846591999675)
        flow_range = flow_range.values
        flow_range = np.where(flow_range>maxflow,maxflow,flow_range)
        flow_info['Date/Time']=flow_info['Date/Time'].astype('datetime64[ns]')
        time_start = flow_info['Date/Time'].iloc[0]
        time_end = flow_info['Date/Time'].iloc[1]
        time_step_hr = time_diff_hr(time_start,time_end)
        
    elif (op == 'Generalized'):
        
        if rated_flow is not None:
            # rated_flow = rated_flow
            maxflow= 0.028316846591999675 * rated_flow # cu.ft/sec to cu.m/sec conversion
        else:
            raise ValueError('Provide maximum flow capacity')
        flow_arr=np.linspace(0.05,1,20)
        flow_range= maxflow * flow_arr
    
    if sys_effi is not None:
        sys_effi = sys_effi
    else:
        sys_effi =0.98
    
    """
    flo = get_flow(___)
    pow = get_power(___)
    eff = get_eff(__)
    dict_return = {"power":pow,
                   "eff":eff,
                   "flow":flow}
    return dict_return

    x = func()
    x["power"]
    """
        
    '''    
    D=dia/1000 #Diameter in meters
    
    # Dynamic Viscosity as a function of temperature
    df2= temp[temp.Farenheit == temp_input]
    dyn_visc = df2['Mu'].tolist()[0]
    nu = df2['Nu'].tolist()[0]
    
    #Roughness Coefficient based on piping type
    
    df3=mat[mat.Material == material]
    rough= df3['RoughnessCoefficient'].tolist()[0]
    
    #Relative Roughness
    rela_rough = rough/dia
    
    #flow_arr=np.linspace(0.05,1,20)
    
    #flow_range= maxflow * flow_arr
    #flow_range = flow_info['Actual (cfs)'] * 0.028316846591999675
    #flow_range = flow_range.values
    #Reynolds Coefficient
    
    #Re=(4 * flow * D)/(dyn_visc * math.pi * D**2)
    
    Re= (4*flow_range)/(math.pi*D*nu)
    
    #Friction factor
    
    f= 0.11 * ((rela_rough) + (68 / Re)) ** (1/4)
    
    
    
    velo=(4*flow_range)/(math.pi * D**2)
    '''
    df1=df[(head > df.Start) & (head <= df.End)]
    
    if turb is not None:
        tur_name = turb
    else:
        tur_name = df1['Turbine'].to_string(index=False).strip()
    k2= df1['k2'].tolist()[0]
    k1=0.41
    Rm=4.5



        
    if (system=='pipe'):
        '''
        h_f=f*(L*v**2)/(d*2*g) or h_f =0.0311*(f*L*Q**2)/d**3
        f = friction factor (user input)
        L = Length of pipe (user input) (m)
        d = pipe diameter (m)
        v = velocity (m/sec^2)
        g = acceleration due to gravity (constant)
        
        '''
        #h_f = f*(length*velo**2)/(D*2*g)
        h_f = 0.05* flow_range
        #h_f=0
        '''
        Calculating for inclined pipe
        Pressure Drop
        del_p = rho*g*(h_f - length * sin(angle))
        h_f_inc = (del_p/(rho *g)) + (length * sin(angle)) #angle is measured in degrees
        '''
        
        #del_p = (rho * g)*(h_f - (length * math.sin(angle)))
        #p_diff = (f*length*rho*g*velo**2)/(D*2*g)
        #h_f_inc = (del_p/(rho *g)) + (length * math.sin(angle))
        
    elif (system=='canal'):
        
        h_f= 0.2* flow_range
        #h_f=0 #Special cases for Dams
    elif (system=='reservoir'):
        h_f= 0.001* flow_range # 0.1% head_loss considered else max(h_f) will not be iterable
    
    '''
    if (min(head-h_f)<0):
        message="Check value(s) for diameter and Flow"
        Tk().withdraw()
        messagebox.showinfo("Error",message)
       
        raise SystemExit
    '''    
    
    '''
    Head Loss Calculation
    
    http://fluid.itcmp.pwr.wroc.pl/~znmp/dydaktyka/fundam_FM/Lecture11_12.pdf
    '''
    
    '''
    Eauation P = [rho*g*Q*[H_g-(h_hydr+h_tail)]*e_t*e_g*(1-l_trans)*(1-l_para)]
    rho Specific density of water (constant 1000 kg/m^3)
    g Acceleartion due to gravity (constant 9.81 m/sec^2)
    H_g Gross head (m)
    h_hydr Hydraulic loss (m)
    h_tail Tail effect associated with the flow (m)
    e_t Turbine efficiency (%)
    e_g Generator efficiency (%)
    l_trans Transformer Losses
    l_para Parasitic electricity losses
    ''' 
    
    effi_cal=[] #Contains the range of efficiencies for the flow range
    
    '''
    if tur==francis
        efficiency = effi_francis()
        
    power = 
    '''
    
    if (tur_name=='Francis turbine'):
        
        reac_runsize = k1*(maxflow)**(0.473)
        
        speci_speed = k2*abs((head-max(h_f)))**(-0.5)
        
        speed_ad = ((speci_speed - 56)/256)**2
        run_size = (0.081 + speed_ad)*(1-(0.789*(reac_runsize**(-0.2))))
        peak_eff = (0.919 - speed_ad + run_size)-0.0305 + 0.005*Rm
        peak_eff_flow = 0.65*maxflow*(speci_speed**0.05)
        full_load_eff_drop = 0.0072 *(speci_speed)**0.4
        eff_full_load = (1-full_load_eff_drop)*peak_eff
        
        for i in range(len(flow_range)):
            if (peak_eff_flow > flow_range[i]):
                #print('yes')
                effi = (1-(1.25*((peak_eff_flow- flow_range[i])/peak_eff_flow)**(3.94 - 0.0195 *speci_speed)))*peak_eff
                
                if (effi <= 0):
                    effi = 0
                effi_cal.append(effi)
                
            else:
                #print('no')
                effi = peak_eff- (((flow_range[i] - peak_eff_flow)/(maxflow - peak_eff_flow)**2)*(peak_eff - eff_full_load))
                if (effi <= 0):
                    effi = 0
                effi_cal.append(effi)
                
                
        power = abs(flow_range * (head - h_f) * effi_cal * sys_effi * g * rho)
        
        power = power/10**6 
        val_min=0
        
    elif (tur_name=='Kaplan turbine' or  tur_name =='Propeller turbine'):
        # print('Entering Kaplan Calculation Module')
        reac_runsize = k1*(maxflow)**(0.473)
        
        speci_speed = k2*abs((head - max(h_f)))**(-0.5)
        speed_ad= ((speci_speed-170)/700)**2
        run_size = (0.095 + speed_ad)*(1-(0.789*(reac_runsize**(-0.2))))
        peak_eff = (0.905 - speed_ad + run_size)-0.0305 + 0.005*Rm
        
        if (tur_name=='Kaplan turbine'):
           peak_eff_flow = 0.75 * maxflow
           
           effi_cal = (1- 3.5*((peak_eff_flow - flow_range)/peak_eff_flow)**6)*peak_eff
           #print(effi_cal)
           effi_cal = np.where(effi_cal <=0 , 0, effi_cal)
        elif (tur_name=='Propeller turbine'):
            peak_eff_flow = maxflow
            
            effi_cal = (1-1.25((peak_eff_flow - flow_range)/peak_eff_flow)**1.13)*peak_eff
            effi_cal = np.where(effi_cal <=0 , 0, effi_cal)
        power = abs(flow_range * (head - h_f) * effi_cal * sys_effi * g * rho) 
        power=power/10**6
        val_min=0
        #pmax = max(power)
        
        #pmin = min(i for i in power if i > val_min)
        
    elif(tur_name=='Pelton turbine' or tur_name=='Turgo turbine'):
        num = 5
        rot_sp = 31*(abs((head-max(h_f)))*(maxflow/num))**0.5
        out_run_dia = (49.4*(abs((head-max(h_f)))**0.5)*num**0.02)/rot_sp
        tur_peak_eff = 0.864* out_run_dia**0.04
        peak_eff_flow = (0.662+0.001*num)*maxflow
        effi_pelo = (1-((1.31+0.025*num)*(abs(peak_eff_flow - flow_range)/(peak_eff_flow))**(5.6+0.4*num)))*tur_peak_eff    
        if (tur_name=='Pelton turbine'):
            effi_cal = effi_pelo
        elif(tur_name=='Turgo turbine'):
            effi_cal = effi_pelo - 0.03
        effi_cal = np.where(effi_cal <=0 , 0, effi_cal)
        power = abs(flow_range * (head - h_f) * effi_cal * sys_effi * g * rho)
        power = power/10**6
        val_min=0
        
       
    elif(tur_name=='Crossflow turbine'):
        peak_eff_flow = maxflow
        effi = 0.79 - 0.15 *((peak_eff_flow - flow_range)/peak_eff_flow)-1.37*((peak_eff_flow - flow_range)/(peak_eff_flow))**(14)
        effi_cal=effi
        effi_cal = np.where(effi_cal <=0 , 0, effi_cal)
        power = abs(flow_range * (head - h_f) * effi_cal * sys_effi * g * rho)
        power=power/10**6
        val_min=0
        
    '''
    def cross_flow(maxflow,flow_range):
        
        peak_eff_flow = maxflow
        effi = 0.79 - 0.15 *((peak_eff_flow - flow_range)/peak_eff_flow)-1.37*((peak_eff_flow - flow_range)/(peak_eff_flow))**(14)
        effi_cal=effi
        effi_cal = np.where(effi_cal <=0 , 0, effi_cal)
    return effi_cal

    def turb(__):
        
        return effi_cal
    
    def cal_power(flowrange, head, h_f,sys_effi,effi_calg,ro):
        
        p = ....
        return power
    for i in range(len(power)):
        if (power[i] > per_75):
            power[i] = per_75
    '''
    if energy_cost is not None:
        cent = energy_cost
    else:
        cent = 0.04
    
    if cost is not None:
        const = cost
    else:
        const = 4.1 #Million $/kWh
    turb_cap = np.percentile(power,75)
    power=np.where(power>turb_cap,turb_cap,power) #Changed for VRG
    #np.savetxt('power_IFP_cap1.csv',power)
    #np.savetxt('turbine_effi.csv',effi_cal)
    effi_cal = [i * 100 for i in effi_cal]
    #flow_info['Power (MW)'],flow_info['Efficiency (%)']=[power,effi_cal]
    #flow_info = flow_info.drop(['Indic'],axis=1)
    #flow_info.to_csv('File_out_{}_{}_to_{}.csv'.format(site_no,begin_date,end_date),index=False)
    
    if (op == 'Timeseries'):
        #flow_info = flow_info.drop(['Average (cfs)'],axis=1)
        flow_range = flow_range/0.028316846591999675
        flow_info['Power (MW)'],flow_info['Efficiency (%)'],flow_info['Average_clipped (cfs)']=[power,effi_cal,flow_range]
        # flow_info.to_csv('C:\Work\My_Code\Files\.csv'.format(site_no,begin_date,end_date),index=False)
        mwh = power * time_step_hr # MWh calculation
        tot_mwh = sum(mwh)  # Total Energy
    elif (op == 'Generalized'):
        valu= []
        for i in range(len(power)-1):
            create = ((power[i]+power[i+1])/2)
            valu.append(create)
        mwh = sum(valu)  # MWh calculation  
        tot_mwh = sum(valu) * 438 * 0.8 # Total Energy
        
    effi_cal = np.asarray(effi_cal)    
    revenue = (tot_mwh *10**3)*(cent/100) #Calculating revenue in Dollars
    const_cost = turb_cap*const #Construction cost
    #h_f= 10.67 *(((L_1 - L_2)* flow**1.85)/(C**1.85 * D**4.87))
    
    return revenue, const_cost, tot_mwh, effi_cal, power, op
   

'''
Possiblity of adding plots in future

#Making plot on 21 points (0,1)
'''
'''
effi_cal.insert(0,0)
flow_arr = np.insert(flow_arr,0,0)
power = np.insert(power,0,0)

flow_arr = flow_range/maxflow
fig,ax=plt.subplots()
#ax = fig.add_subplot(1,1,1)
ax.plot(flow_arr,effi_cal,'g-',marker='*',markerfacecolor='b',markersize=7)
vals = ax.get_xticks()
ax.set_xticklabels(['{:,.0%}'.format(x) for x in vals])
ax.grid(True, axis='both', color='k',linestyle='--',alpha=0.4)
ax.set_xlabel("Percentage of rated flow (%)")
ax.set_ylabel("Efficiency",color='g')

ax1=ax.twinx()
ax1.plot(flow_arr,power,'b-',marker='o',markerfacecolor='r',markersize=7)
vals = ax1.get_xticks()
ax1.set_xticklabels(['{:,.0%}'.format(x) for x in vals])
ax1.grid(True, axis='both', color='k',linestyle='--',alpha=0.4)
ax1.set_xlabel("Percentage of rated flow (%)")
ax1.set_ylabel("Power (MW)",color='b')
plt.show()
'''
'''
Head suggesting the types of turbines to be used.
https://theconstructor.org/practical-guide/hydraulics-lab/turbines-pumps/factors-affecting-selection-hydraulic-turbine/30826/
print('Calculated Power Output:', power, '(W) \n')
'''
'''

Equations:

Hydraulic head loss (Thomas Paper)

h_f= 10.67 *(((L_1 - L_2)* flow**1.85)/(C**1.85 * D**4.87))

h_f: hydraulic head loss (m)
L_1: starting point of penstock
L_2: end point of penstock
flow: volumetric flowrate (m^3/s)
C: roughness coefficient
D: internal pipe diameter (m)
'''

'''
text = {'Start':[0.5,10,60,150,350,2000],'End':[10,60,150,350,2000,5000],'Suitable Turbine':['Kaplan Turbine','Kaplan Turbine','Francis Turbine','Francis Turbine','Pelton Turbine','Pelton Turbine'],'k2':[800,800,600,600,0,0]}

def efficiency(tur_name):
    
'''