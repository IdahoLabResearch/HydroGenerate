# -*- coding: utf-8 -*-
"""
Created on Sun May 30 19:12:46 2021
@author: Bhaskar
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 14:14:12 2021
@author: MITRB
"""

'''
Python API
'''

import requests
from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
from datetime import datetime
import numpy as np

class APIError(Exception):
    """An API Error Exception"""

    def __init__(self, status,message,info):
        self.status = status
        self.message = message
        self.info = info
   
    
    def __str__(self):
        
        return "APIError: status={}, Message={}.\nCheck {} for more information".format(self.status,self.message,self.info)

def API_response(status):
    API = {'Message':['Continue','Switching Protocol','Processing','Early Hints','OK','Created','Accepted','Non-Authoritative Information',
                     'No Content','Reset Content','Partial Content','Multi-Status','Already Reported','IM Used','Multiple Choice',
                     'Moved Permanently','Found','See Other','Not Modified','Temporary Redirect','Permanent Redirect','Bad Request',
                     'Unauthorized','Payment Required','Forbidden','Not Found','Method Not Allowed','Not Acceptable','Proxy Authentication Required',
                     'Request Timeout','Conflict','Gone','Length Required','Precondition Failed','Payload Too Large','URI Too Long',
                     'Unsupported Media Type','Range Not Satisfiable','Expectation Failed','I am a teapot','Misdirected Request','Unprocessable Entity',
                     'Locked','Failed Dependency','Too Early','Upgrade Required','Precondition Required','Too Many Requests','Request Header Fields Too Large',
                     'Unavailable for Legal Reasons','Internal Server Error','Not Implemented','Bad Gateway','Service Unavailable','Gateway Timeout',
                     'HTTP Version Not Supported','Variant Also Negotiates','Insufficient Storage','Loop Detected','Not Extended','Network Authentication Required'],
             'Code':[100,101,102,103,200,201,202,203,204,205,206,207,208,226,300,301,302,303,304,307,308,
                     400,401,402,403,404,405,406,407,408,409,410,411,412,413,414,415,416,417,418,421,422,423,424,425,
                     426,428,429,431,451,500,501,502,503,504,505,506,507,508,510,511]}
    df = pd.DataFrame.from_dict(API)
    df_new = df[status == df['Code']]
    message = df_new['Message'].tolist()[0]
    return message
def api_code(site_no,begin_date,end_date,data_type):
    
    '''
    When we need data at 15min interval
    '''
    if(data_type == "15min"):
        
        url="https://nwis.waterservices.usgs.gov/nwis/iv/?format=rdb&sites={}&startDT={}&endDT={}&parameterCd=00060&siteStatus=all".format(site_no,begin_date,end_date)
    
    #When we need daily data
    elif(data_type == "Daily"):
        url="https://nwis.waterdata.usgs.gov/nwis/dv?cb_00060=on&format=rdb&site_no={}&referred_module=sw&period=&begin_date={}&end_date={}".format(site_no,begin_date,end_date)
    
    else:
        raise ValueError("Please make appropriate selection")
        sys.exit(0)
        
    info ='https://developer.mozilla.org/en-US/docs/Web/HTTP/Status'
    response = requests.get(url)
    if response.status_code !=200:
        message = API_response(response.status_code)
        raise APIError(response.status_code,message,info)
    return url

site_no='11251000'
begin_date = '2012-01-01'
end_date = '2012-12-31'

data_type = str(input("Data Options (15min/Daily): "))

if (data_type=='15min'):
    type = str((input("Do you need hourly data (Y/N): ")))
    if (type=='Y'):
        request = 'hourly'
    else:
        request=''
else:
    request=''
    



url = api_code(site_no,begin_date,end_date,data_type)

def data_missing(begin_date,end_date,data_type):
    
    new_begin = datetime.strptime(begin_date,'%Y-%m-%d')
    new_end = datetime.strptime(end_date,'%Y-%m-%d')
    days = (new_end - new_begin).days + 1
    
    if (data_type=='15min'):
        data_len = days*96
    else:
        data_len = days
    return data_len

data_len = data_missing(begin_date,end_date,data_type)       

html = urlopen(url).read()
soup = BeautifulSoup(html,"html.parser")

for script in soup(["script","style"]):
    script.extract()

text=soup.get_text()

tempu=[x for x in text.strip('\n').split('\n') if not x.startswith('#')][2:]

if(data_type == '15min'):
    
    '''
    Use when we need 15 min data
    '''
    data1="Agency,Site_ID,Date/Time,TZ,Average (cfs),Indic\n"+"\n".join([','.join([x for x in y.split('\t')]) for y in tempu])

    '''
    Use when we need daily data
    '''
else:
    data1="Agency,Site_ID,Date/Time,Average (cfs),Indic\n"+"\n".join([','.join([x for x in y.split('\t')]) for y in tempu])

test=StringIO(data1)

flow_info=pd.read_csv(test,sep=",")

if (flow_info.shape[0]<=1):
    raise ValueError('Empty file returned, check url:\n{}'.format(url))

'''
Working on Missing Data
'''

if(data_len!=len(flow_info['Date/Time'])):
    
    print('There is data missing in the NWIS database')
    flow_info['Date/Time'] = pd.to_datetime(flow_info['Date/Time'])
    
    if(data_type == '15min'):
        flow_info = flow_info.loc[~flow_info['Date/Time'].duplicated(),:].set_index('Date/Time').asfreq('15min').reset_index() #This handles if there are any duplicates in the 'Date/Time' column
        flow_info[flow_info[['Agency','Site_ID','TZ','Indic']]=='']=np.NaN
        flow_info = flow_info.mask(flow_info=='NaN').ffill()
        print('Missing data filled')
    else:
        flow_info = flow_info.loc[~flow_info['Date/Time'].duplicated(),:].set_index('Date/Time').asfreq('1D').reset_index() #This handles if there are any duplicates in the 'Date/Time' column
        flow_info[flow_info[['Agency','Site_ID','Indic']]=='']=np.NaN
        flow_info = flow_info.mask(flow_info=='NaN').ffill()
        print('Missing data filled')
        
'''
If requested data is hourly (Available only if 15min data is chosen)
'''

if (request=='hourly'):
    flow_info['Date/Time'] = pd.to_datetime(flow_info['Date/Time'])
    flow_info=flow_info.set_index('Date/Time')
    flow_info = flow_info.resample('60min').mean()
    flow_info=flow_info.reset_index()

    
'''
Saving Dataframe as csv
'''

flow_info.to_csv("C:\Work\My_Code\Files\{}_{}_{}.csv".format(site_no,begin_date,data_type),index=False)


'''
flow_info['Date/Time'] = pd.to_datetime(flow_info['Date/Time'])
flow_info = flow_info.set_index('Date/Time').asfreq('15min').reset_index()
'''