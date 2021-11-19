# -*- coding: utf-8 -*-
"""
Created on Wed May  5 09:47:41 2021

@author: MITRB
"""

import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
#import html2text

def api_code(site_no):
    '''
    When we need data at 15min interval
    '''
    
    huc_url="https://waterservices.usgs.gov/nwis/iv/?format=rdb&huc={}&parameterCd=00060&siteStatus=all".format(site_no)
    #"https://nwis.waterservices.usgs.gov/nwis/iv/?format=rdb&sites={}&startDT={}&endDT={}&parameterCd=00060&siteStatus=all".format(site_no,begin_date,end_date)
    
    '''
    When daily data is required
    '''
    #url="""https://nwis.waterdata.usgs.gov/nwis/dv?cb_00060=on&format=rdb&site_no={}&referred_module=sw&period=&begin_date={}&end_date={}""".format(site_no,begin_date,end_date)
    
    response = requests.get(huc_url)
    if response.status_code !=200:
        raise ApiError('GET /tasks/ {}'.format(response.status_code))
    return huc_url

site_no='17050104'
#site_no='17040201'
#begin_date = '2019-01-01'
#end_date = '2019-12-31'
#request=''
huc_url = api_code(site_no)

html = urlopen(huc_url).read()
soup = BeautifulSoup(html,"html.parser")

for script in soup(["script","style"]):
    script.extract()

text=soup.get_text()

tempu=[x for x in text.strip('\n').split('\n') if x.startswith('#    USGS')]

#data1="Agency,Site_ID,State\n"+"\n".join([','.join([x for x in y.split('#    ')]) for y in tempu])
data1="Agency,Site_ID,Address,State\n"+"\n".join([','.join(temp.lstrip("# ").split(" ")[:3])+' '+' '.join(temp.lstrip("# ").split(" ")[3:]) for temp in tempu])

test=StringIO(data1)

info=pd.read_csv(test,sep=",")


print("\n\nData for the following {} sites were obtained:".format(len(info)),"\n\n-----------------------------------------------------\n\n",info)

site_no= str(input("Enter the desired Site_ID: "))
begin_date = str(input("Enter the desired start date (formart YYYY-MM-DD): "))
end_date = str(input("Enter the desired end date (formart YYYY-MM-DD): "))
request = str(input("Do you want hourly data (Y/N): "))

def api_code_data(site_no,begin_date,end_date,request):
    if (request=='N'):
    
        url = "https://nwis.waterservices.usgs.gov/nwis/iv/?format=rdb&sites={}&startDT={}&endDT={}&parameterCd=00060&siteStatus=all".format(site_no,begin_date,end_date)
    else:
        url = "https://nwis.waterdata.usgs.gov/nwis/dv?cb_00060=on&format=rdb&site_no={}&referred_module=sw&period=&begin_date={}&end_date={}".format(site_no,begin_date,end_date)


    response = requests.get(url)
    if response.status_code !=200:
        raise ApiError('GET /tasks/ {}'.format(response.status_code))
    return url


url = api_code_data(site_no,begin_date,end_date,request)

html = urlopen(url).read()
soup = BeautifulSoup(html,"html.parser")

for script in soup(["script","style"]):
    script.extract()

text=soup.get_text()

tempu=[x for x in text.strip('\n').split('\n') if not x.startswith('#')][2:]

if (request=='N'):
    
    data2="Agency,Site_ID,Date/Time,TZ,Average (cfs),Indic\n"+"\n".join([','.join([x for x in y.split('\t')]) for y in tempu])

else:
    
    data2="Agency,Site_ID,Date/Time,Average (cfs),Indic\n"+"\n".join([','.join([x for x in y.split('\t')]) for y in tempu])
    
test=StringIO(data2)

flow_info=pd.read_csv(test,sep=",")

if (flow_info.shape[0]<=1):
    raise ValueError('Empty file returned, check url:\n{}'.format(url))
    
if (request=='Y'):
    flow_info['Date/Time'] = pd.to_datetime(flow_info['Date/Time'])
    flow_info=flow_info.set_index('Date/Time')
    flow_info = flow_info.resample('60min').mean()
    flow_info=flow_info.reset_index()