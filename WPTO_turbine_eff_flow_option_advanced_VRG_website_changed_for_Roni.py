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
#from data_prep_Roni import flow_info
#from getting_data_from_usgs import *

#from MLR import flow_info

#flow_info = pd.read_csv(r'C:\Work\My_Code\mode.csv')


site_no='Sandbar_11292900_design_flow_clipped_new_head_loss'
begin_date = '2019-01-01'
end_date = '2019-12-31'


#Declaring some constants

g = 9.81
rho = 1000
turb_cap = 1.1 #Turbine nameplate capacity in MW '''Narrows 1 12 MW''' '''IFP(Lower) 8.6 MW''' #16.2 MW for Sandbar #1.1 MW Roni's Work
diff_m = 32 #ft '''263 ft for Yuba River Dam''' '''19ft IFP (lower)''' #365ft for Sandbar #32ft Roni's Work

'''
1 ft = 0.3048m # Ft to m conversion
'''

#flow_info = pd.read_csv(r'C:\Work\My_Code\mean.csv')
#flow_info = pd.read_csv(r'C:\Work\My_Code\Files\11292900_2019-01-01.csv')
#h_f = pd.read_csv(r'C:\Work\My_Code\Files\Net_h_f_new.csv')
#df = pd.read_excel(r'C:\Work\WPTO\turbine.xlsx')
#temp = pd.read_excel(r'C:\Work\WPTO\temp.xlsx')
#mat = pd.read_excel(r'C:\Work\WPTO\material.xlsx')
#flow_info = pd.read_excel(r'C:\Work\VRGHydro\SHELLY_5_4_12_5_22_13.xlsx')
#flow_info = pd.read_excel(r'C:\Work\VRGHydro\Data.xlsx')
#flow_info = pd.read_excel(r'C:\Work\VRGHydro\usgs_profile.xlsx')
#flow_info = pd.read_excel(r'C:\Work\VRGHydro\test.xlsx')
#flow_info = pd.read_excel(r'C:\Work\VRGHydro\USGS_bulb.xlsx')
#flow_info = pd.read_csv(r'C:\Work\VRGHydro\{}'.format(filename))
flow_info = pd.read_csv(r'C:\Work\My_Code\Files\Flow_upstream_power_efficiency_input.csv')
root = Tk()
root.title("HydroPower Module")

# Add a grid
mainframe = Frame(root)
mainframe.grid(column=0,row=0, sticky=(N,W,E,S) )
mainframe.columnconfigure(0, weight = 1)
mainframe.rowconfigure(0, weight = 1)
mainframe.pack(pady = 100, padx = 100)

tkvar_flow = DoubleVar(root)
tkvar_head = DoubleVar(root)
tkvar_effi = DoubleVar(root)
tkvar_maxflow = DoubleVar(root)
tkvar_effi_sys = DoubleVar(root, value = 0.98)
tkvar_turb = StringVar(root)
tkvar_type = StringVar(root)
#tkvar_dia = DoubleVar(root)
#tkvar_len = DoubleVar(root)
#tkvar_mat = StringVar(root)
tkvar_con = DoubleVar(root, value=4.1)
tkvar_cen = DoubleVar(root, value =5)
tkvar_op = StringVar(root)
#tkvar_grav = DoubleVar(root)

# tkvar_button0 = StringVar(root)
# tkvar_button1 = StringVar(root)
# tkvar_button2 = StringVar(root)
# tkvar_button3 = StringVar(root)
# tkvar_button4 = StringVar(root)
# tkvar_button5 = StringVar(root)
# tkvar_button6 = StringVar(root)
# tkvar_button7 = StringVar(root)


#Gui construction
Label(mainframe, text="Calculation of Hydropower as a Function of Flow").grid(row = 1, column = 1)

options=['','From File','Generalized']
popupMenu = OptionMenu(mainframe, tkvar_op, *options)
Label(mainframe, text="Data Source").grid(row = 3, column = 1)
popupMenu.grid(row = 4, column = 1)
tkvar_op.set(options[0])

Label(mainframe, text="Enter Max. Flow Rate (cu.ft/sec) \n(Required for Generalized Data Source)").grid(row = 7, column = 5)
maxflow = Entry(mainframe, textvariable = tkvar_maxflow)

maxflow.grid(row = 8, column = 5)

'''
Label(mainframe, text="Enter Gross Head Height at site (m)").grid(row = 3, column = 2)
head = Entry(mainframe, textvariable = tkvar_head)
head.grid(row=4,column=2)

'''
'''
Label(mainframe, text="Enter Turbine Efficiency (%)").grid(row = 3, column = 3)
effi = Entry(mainframe, textvariable = tkvar_effi)
effi.grid(row=4,column=3)
'''
'''
Label(mainframe, text="Enter Max. Flow (cfs)").grid(row = 3, column = 3)
effi = Entry(mainframe, textvariable = tkvar_maxflow)
effi.grid(row=4,column=3)
'''
Label(mainframe, text="Enter System Efficiency (%)").grid(row = 3, column = 3)
effi_sys = Entry(mainframe, textvariable = tkvar_effi_sys)
effi_sys.grid(row=4,column=3)

Label(mainframe, text="Acceleration due to gravity (m/sec^2)").grid(row = 3, column = 4)
Label(mainframe, text="9.81").grid(row = 4, column = 4)

Label(mainframe, text="Specific Density of water (kg/m^3)").grid(row = 3, column = 5)
Label(mainframe, text="1000").grid(row = 4, column = 5)

options=['Default','Kaplan turbine','Francis turbine', 'Pelton turbine', 'Propellor turbine', 
         'Turgo turbine', 'Crossflow turbine']
popupMenu = OptionMenu(mainframe, tkvar_turb, *options)
Label(mainframe, text="Turbine").grid(row = 5, column = 2)
popupMenu.grid(row = 6, column = 2)
tkvar_turb.set(options[0])

options=['','reservoir','pipe','canal']
popupMenu = OptionMenu(mainframe, tkvar_type, *options)
Label(mainframe, text="Structure").grid(row = 5, column = 3)
popupMenu.grid(row = 6, column = 3)
tkvar_type.set(options[0])
'''
Label(mainframe, text="Diameter (in) (Valid for selection type pipe)").grid(row = 5, column = 4)
dia = Entry(mainframe, textvariable = tkvar_dia)
dia.grid(row=6,column=4)

options=['','Cast Iron','Commercial Steel and Wrought Iron', 'Concrete', 'Drawn Tubing', 
         'Galvanized Iron', 'Plastic/Glass', 'Riveted Steel','HDPE']
popupMenu = OptionMenu(mainframe, tkvar_mat, *options)
Label(mainframe, text="Piping Material").grid(row = 5, column = 5)
popupMenu.grid(row = 6, column = 5)
tkvar_mat.set(options[0])
'''
Label(mainframe, text="Construction Cost (million $/MW)").grid(row = 7, column = 3) 
con = Entry(mainframe, textvariable = tkvar_con)
con.grid(row=8,column=3)

Label(mainframe, text="Power Sale Price (cents/kWh)").grid(row = 7, column = 4) 
cen = Entry(mainframe, textvariable = tkvar_cen)
cen.grid(row=8,column=4)

'''
Label(mainframe, text="Length (m) (Valid for selection type pipe").grid(row = 5, column = 5)
length = Entry(mainframe, textvariable = tkvar_len)
length.grid(row=6,column=5)
'''

# Returns the values from the gui
def valcal(*args):
     button= ttk.Button(root, text="Calculate", command=root.quit)
     button.pack()
     root.mainloop()
     
     maxflow=tkvar_maxflow.get()
     op=tkvar_op.get()
     #head=tkvar_head.get()
     #maxflow=tkvar_maxflow.get()
     effi_sys=tkvar_effi_sys.get()
     system=tkvar_type.get()
     #dia=tkvar_dia.get()
     #material = tkvar_mat.get()
     const = tkvar_con.get()
     cent = tkvar_cen.get()
     turb = tkvar_turb.get()
     
     #length=tkvar.len.get()
     if (op == ''):
         raise ValueError('Select Data Source')
         sys.exit(0)
     if (op == 'Generalized') and (maxflow == 0):
         raise ValueError('Enter flow information')
         sys.exit(0) 
     if (system == ''):
         raise ValueError('Select type of modernization')
         sys.exit(0)
     #if (material == ''):
      #  raise ValueError('Select Material')
      #  sys.exit(0) 
     #if (system =='pipe') and (dia == 0):
      #   raise ValueError('Enter pipe diameter')
       #  sys.exit(0)
     #if (effi >= 1) or (effi <= 0):
         #raise ValueError('Efficiency ranges between 0-0.99')
         #sys.exit(0)
     if (effi_sys >= 1) or (effi_sys <= 0):
         raise ValueError('Loss ranges between 0-0.99')
         sys.exit(0)
     root.destroy()
     
     
     return(maxflow,op,effi_sys,system,const,cent,turb)
 
(maxflow,op,effi_sys,system,const,cent,turb)=valcal()
'''
This maintains the turbine selection data based on head

Head suggesting the types of turbines to be used.
https://theconstructor.org/practical-guide/hydraulics-lab/turbines-pumps/factors-affecting-selection-hydraulic-turbine/30826/
'''

turb_data = {'Head':['Very low head','Low head','Medium head','High head',
                     'Very high head','Very high head'],
             'Start':[0.5,10,60,150,350,2000],
             'End':[10,60,150,350,2000,5000],
             'Suitable Turbine':['Kaplan turbine','Kaplan turbine',
                                 'Francis turbine','Francis turbine',
                                 'Pelton turbine','Pelton turbine'],
             'k2':[800,800,600,600,0,0]}

#Converting the dictionary to DataFrame

df = pd.DataFrame(data=turb_data)
#max_flow_val = 569 #Provide design flow in cfs
diff_m = diff_m * 0.3048 # converting ft. to m
head=abs(diff_m)
#length = length*1609.34 #Converting mi to m

if head <= 0.6:
    #raise ValueError('Head height too low for small-scale hydropower')
    message="Head height too low for small-scale hydropower"
    # Ref: https://www.energy.gov/energysaver/planning-microhydropower-system
    Tk().withdraw()
    messagebox.showinfo("Error",message)
    #raise ValueError('Head height too low for small-scale hydropower')
    raise SystemExit
#dia = dia * 25.4 # converting inches to mm
def time_diff_hr(dt1,dt2):
    timedel = dt2 - dt1
    time_step_hr = (timedel.days*24*3600 + timedel.seconds)/3600
    return time_step_hr

if (op == 'From File'):
    flow_info['Average (cfs)']=flow_info['Average (cfs)'].replace(['Ice','Mtn','Bkw','NaN','--','Dis','Dry',
                                                                   '***','Eqp','Rat','ZFI','Ssn'],0)
    #flow_info['Average (cfs)']=flow_info['Average (cfs)'].replace('NaN',0)
    #flow_info['Average (cfs)']=flow_info['Average (cfs)'].astype(int)
    flow_info = flow_info.dropna(subset=['Average (cfs)'])
    #flow_info=flow_info[flow_info['Average (cfs)'] !=0] 
    maxflow = max(flow_info['Average (cfs)'])
    
    '''
    1 cu.ft/sec = 0.028316846591999675 cu.m/sec
    '''
    #maxflow= 0.028316846591999675 * maxflow # cu.ft/sec to cu.m/sec conversion
    maxflow_val = max(flow_info['Average (cfs)']) + 0.01*max(flow_info['Average (cfs)'])
    maxflow = 0.028316846591999675*maxflow_val #Calcualted design_flow 569 cfs for sandbar
    flow_range = flow_info['Average (cfs)'] * (0.028316846591999675)
    flow_range = flow_range.values
    #flow_range = np.where(flow_range>maxflow,maxflow,flow_range)
    flow_info['Date/Time']=flow_info['Date/Time'].astype('datetime64[ns]')
    time_start = flow_info['Date/Time'].iloc[0]
    time_end = flow_info['Date/Time'].iloc[1]
    time_step_hr = time_diff_hr(time_start,time_end)
    
elif (op == 'Generalized'):
    
    maxflow= 0.028316846591999675 * maxflow # cu.ft/sec to cu.m/sec conversion
    flow_arr=np.linspace(0.05,1,20)
    flow_range= maxflow * flow_arr
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
if (turb == 'Default'):
    tur_name = df1['Suitable Turbine'].to_string(index=False).strip()
    #print("Default Selected")
else:
    tur_name = turb
    #print("Override Performed")
k2= df1['k2'].tolist()[0]
k1=0.41
Rm=4.5



    
if (system=='pipe'):
    '''
    h_f=f*(L*v**2)/(d*2*g)
    f = friction factor (user input)
    L = Length of pipe (user input) (m)
    D = pipe diameter (m)
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
    #h_f = h_f['Average (cfs)']

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

if (tur_name=='Francis turbine'):
    #print('Entering Francis Calculation Module')
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
            #print(effi)
            if (effi <= 0):
                effi = 0
            effi_cal.append(effi)
        else:
            #print('no')
            effi = peak_eff- (((flow_range[i] - peak_eff_flow)/(maxflow - peak_eff_flow)**2)*(peak_eff - eff_full_load))
            effi_cal.append(effi)
    power = abs(flow_range * (head - h_f) * effi_cal * effi_sys * g * rho)
    #print(power)
    #print(effi_cal)
    power = power/10**6 
    val_min=0
    #pmax = max(power)
    #pmin = min(power)
    
    #pmin = min(i for i in power if i > val_min)
    
    #print(pmax)
    #print(pmin)
    
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
    power = abs(flow_range * (head - h_f) * effi_cal * effi_sys * g * rho) 
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
    power = abs(flow_range * (head - h_f) * effi_cal * effi_sys * g * rho)
    power = power/10**6
    val_min=0
    #pmax = max(power)
    
    #pmin = min(i for i in power if i > val_min)
   
elif(tur_name=='Crossflow turbine'):
    peak_eff_flow = maxflow
    effi = 0.79 - 0.15 *((peak_eff_flow - flow_range)/peak_eff_flow)-1.37*((peak_eff_flow - flow_range)/(peak_eff_flow))**(14)
    effi_cal=effi
    effi_cal = np.where(effi_cal <=0 , 0, effi_cal)
    power = abs(flow_range * (head - h_f) * effi_cal * effi_sys * g * rho)
    power=power/10**6
    val_min=0
    #pmax = max(power)
    
    #pmin = min(i for i in power if i > val_min)
    
#print(max(power))
#print(power)
#per_75 = np.percentile(power,75)
'''
for i in range(len(power)):
    if (power[i] > per_75):
        power[i] = per_75
'''
#print(power)
#print(max(power))
#np.savetxt('power_IFP_non_cap.csv',power)
power=np.where(power>turb_cap,turb_cap,power) #Changed for VRG
#np.savetxt('power_IFP_cap1.csv',power)
#np.savetxt('turbine_effi.csv',effi_cal)
effi_cal = [i * 100 for i in effi_cal]
#flow_info['Power (MW)'],flow_info['Efficiency (%)']=[power,effi_cal]
#flow_info = flow_info.drop(['Indic'],axis=1)
#flow_info.to_csv('File_out_{}_{}_to_{}.csv'.format(site_no,begin_date,end_date),index=False)

if (op == 'From File'):
    flow_info['Power (MW)'],flow_info['Efficiency (%)']=[power,effi_cal]
    flow_info.to_csv('C:\Work\My_Code\Files\Roni_new.csv'.format(site_no,begin_date,end_date),index=False)
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

    
#df1=df[(head > df.Start) & (head <= df.End)]
#plt.plot(flow_range,power)
#output="Calculated Power Output Range: Min: %f (MW) and Max: %f (MW)" %(pmin,pmax)
output = "\n Recommended Nameplate Capacity: %0.2f (MW)" %(turb_cap)
output+= "\n Annual Energy Generation: %0.2f (MWh)" %(tot_mwh)
output+="\n Total Construction cost: $ %0.2f million" %(const_cost)
output+= "\n Annual Revenue: $ %0.2f"%(revenue)
output+="\n Head categorization: %s" %df1['Head'].to_string(index=False).strip()
output+="\n Suggested Tubine: %s" %(tur_name)
#output+="\n Additional Information: %s" %df1['Notes'].to_string(index=False)
#output+="\n Efficiency of turbines = Francis Turbine > Kaplan Turbine > Pelton Turbine"

Tk().withdraw()
messagebox.showinfo("Result",output)

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
'''