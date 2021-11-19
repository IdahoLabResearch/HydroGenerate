# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 12:58:49 2021

@author: MITRB
"""

'''
Send Email as attachement
'''
import smtplib
from email.message import EmailMessage
from hydro_plot_VRG_website import *
#from getting_data_from_usgs import *
from getting_usgs_data_missing_val import *
#from WPTO_turbine_eff_flow_option_advanced_VRG_website import power,effi_cal,flow_info,turb_cap,tot_mwh, tur_name,site_no

#site_no= '11292900'
emailfrom = "bhaskarmitrainl@gmail.com"
emailto = "bhaskar.mitra@inl.gov"
#emailto = "bhaskar.mitra@inl.gov"
fileToSend = "File_out_{}_{}_to_{}.csv".format(site_no,begin_date,end_date)
username = "bhaskarmitrainl@gmail.com"
password = "INL2020*"
pod = "Buchu269101*"

msg = EmailMessage()
msg["From"] = emailfrom
msg["Subject"] = "Requested Hydropower Data"
msg["To"] = emailto
msg.set_content("Dear User,\n\nPlease find the requested hydropower data attached for site {}.\n\nThanks,\n\nIdaho National Laboratory (INL)\n\nHydro Assessment Tool (HAT)".format(site_no))
msg.add_attachment(open(fileToSend, "r").read())

s = smtplib.SMTP_SSL("smtp.gmail.com",465)
#s.connect('smtp.gmail.com',465)
s.ehlo()
s.login(username, password)
text=msg.as_string()
s.sendmail(emailfrom,emailto,text)
s.quit()
print('Email Sent')

