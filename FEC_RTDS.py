import socket
import sys
from time import sleep
import pandas as pd

#Read the csv files
df = pd.read_csv(r'C:\Work\Smart VGI\Data\Dis_load_gen_Data\Outpatient_MW.txt',sep='\t')
df_1 = pd.read_csv(r'C:\Work\Smart VGI\Data\Dis_load_gen_Data\Outpatient_MVAR.txt',sep='\t')

#Create connection request
sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('141.221.118.96', 6000)
sock.connect(server_address)

sock2=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address2 = ('141.221.118.83', 7777)
sock2.connect(server_address2)


#Create a loop to send values at each iteration

for i in range(len(df['MW'])):
    send_var=[]
    vari = df['MW'].iloc[i]
    send_var.append(vari)
    vari_1 = df_1['MVAR'].iloc[i]
    send_var.append(vari_1)
    send_var = send_var.to_bytes(4,byteorder='big')
    sock2.send(send_var)
    

'''


Iold=20.0
I=20.0
count=0
PWbig=(0).to_bytes(4, byteorder='big')
Droopold=0.9931
Droop=0.9895
cycle=0

# read several text files
# import pandas as pd
# df_1 = pd.read_csv(filename)
#df_arr = df1[colname].iloc
# for i in range(len(df_arr)):


while 1==1:

    sock2.send(PWbig)  


    V = sock2.recv(4)
    Vrms=(int.from_bytes(V, byteorder='big'))/100
    
#    print ('Voltage {!r}'.format(Vrms))

#    P = sock.recv(4)
#    PW =int(P)
#    print ('Power {!r}'.format(PW))

#   PWbig=PW.to_bytes(4, byteorder='big')
#    sock2.send(PWbig)    
  
# DROOP

#    cycle += 1
#    Volt[cycle]=Vrms
#    if cycle>10:
#        Voltmedium=Volt(1)+Volt(2)+Volt(3)+Volt(4)+Volt(5)+Volt(6)+Volt(7)+Volt(8)+Volt(9)+Volt(10)
        
#        cycle=0

 #   Vdroop=1-Vrms/237.2
    Vdroop=Droop-Vrms/240
    if Vdroop > 0.005 :
        I=(20.0)*(1-10*Vdroop)
        count=0
        if I < 6:
            I=6
    else:
        if Vdroop > -0.005 :
            count += 1
            if count>5 :
                I=Iold+0.1
                if I>20 :
                    I=20.0
            else :
                I=Iold
        else :
            count=0
            I=(20.0)*(1+10*Vdroop)
            if I < 6:
                I=6
 
    if I>27 :
        I=27
            
        
#    if Vdroop < 0 :
#        I=Iold

    Iold=I
#    I = 13 + random.uniform(0,3)

    if I<10 :
        cmd = '0'+'{:2.1f}'.format(I)
        cmd2=bytes(cmd,'UTF-8')
        
    else:
        cmd = '{:2.1f}'.format(I)
        cmd2=bytes(cmd,'UTF-8')
    print (Vdroop,cmd2)
    sock.send(cmd2)
    sleep(0.1)


sock.close()

'''