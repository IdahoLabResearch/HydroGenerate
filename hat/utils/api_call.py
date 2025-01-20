'''
Copyright 2021, Battelle Energy Alliance, LLC
'''

import requests
import pandas as pd
import numpy as np
import json
import os

# 02.19.2021: Juan Gallego-Calderon
# This is the older url where we were taking the data from. We found that the REST API of water services is more structure so we are going with that.
# url = "https://waterdata.usgs.gov/nwis/dv?cb_00060=on&format=rdb&site_no=13060000&referred_module=sw&period=&begin_date=2020-02-15&end_date=2021-02-14"
    

# class definition
class Stream:
    def __init__(self, huc, site_id, site_name, data, no_data_value):
        self.name = huc
        self.site_id = site_id
        self.site_name = site_name
        self.data = data
        self.no_data_value = no_data_value
        #self.location = 


# The url where the parameter codes (parameterCd) are described: https://help.waterdata.usgs.gov/code/parameter_cd_nm_query?parm_nm_cd=%25discharge%25&fmt=html
# [DONE] TODO: deal with missing values. It looks like USGS makes them -999999.0
# TODO: generalize get_data to take either HUC or site_id
def get_data(query, format = 'json', id_type = 'huc', endpoint='iv', save_data = True, path = os.path.join('data','test.json')):
    '''
    This is the top level function to pull data from the USGS instantaneous value REST service. The 15-min data includes water discharge in cfs and it is requested by HUC codes. 
    The function requests a json object that contains several sites (discretize by site_id). The function returns a list of objects of the type stream_gage class (see class description above)
    Inputs:
    - query: dictionary that contains the information needed for the request: id (HUC code), start_date, end_date
    - format: output format from REST. Default is JSON.
    - id_type: type of site requested. Default is HUC; other option is "sites"
    - save_data: boolean to whether or not save the json response to a .txt file
    '''
    
    if endpoint == 'iv':
        if id_type == 'huc' or id_type == 'sites':
            base_url=f"https://waterservices.usgs.gov/nwis/iv/?format={format}&{id_type}={query['id']}&startDT={query['start_date']}&endDT={query['end_date']}&parameterCd=00060&siteStatus=all"
            #json_filename = os.path.join(path,f"{query['id']}_{query['start_date']}_{query['end_date']}.json")
        elif id_type == 'bBox':
            bBox_str = "".join((query['id'][0],',',query['id'][1],',',query['id'][2],',',query['id'][3]))
            base_url=f"https://waterservices.usgs.gov/nwis/iv/?format={format}&{id_type}={bBox_str}&startDT={query['start_date']}&endDT={query['end_date']}&parameterCd=00060&siteStatus=all"
            #json_filename = os.path.join(path,f"{query['start_date']}_{query['end_date']}.json")
        print(base_url)
        response = requests.get(base_url, verify=False)
        
        if response:
            # Checking for a success response from the API and write response to a text file
            print('Success with data retrieval from API')
            if save_data:
                response_file = path
                with open(response_file, "w") as f:
                    f.write(response.text)
            else:
                pass
            csv_filename = path.replace('json','csv')
            df_respose = format_api_response(response, save_csv=save_data, path=csv_filename) 
            return df_respose
        else:
            print(response.status_code)


def discretize_huc_response(json_obj):
    ''' 
    Returns the meta data for the 
    '''

    data = json_obj.json()
    location = {}
    for var in data['value']['timeSeries']:
        site_name = var['sourceInfo']['siteName']
        #print(var['sourceInfo'])
        site_id = var['sourceInfo']['siteCode'][0]['value']
        location['latitude'] = var['sourceInfo']['geoLocation']['geogLocation']['latitude']
        location['longitude'] = var['sourceInfo']['geoLocation']['geogLocation']['longitude']
        print(f'Site name: {site_name}, site ID:{site_id}')
    return None



def format_api_response(json_obj, save_csv = True, path = os.path.join('data','test.csv')):
    ''' Return a dataframe with the discharge data
    Inputs:
    - json_obj: raw json object from REST.
    Output:
    - df: dataframe with timestamp and discharge data
    '''
    data = json_obj.json()
    df_list = []
    #ßprint(len(data['value']['timeSeries']))
    for var in data['value']['timeSeries']:
        var_name = var['variable']['variableName']
        #print(var['values'][0]['value'])
        df_temp = pd.json_normalize(var['values'][0]['value'])
        df_temp.rename(columns={"value": var_name}, inplace=True)
        df_temp['site_name'] = var['sourceInfo']['siteName']
        df_temp['site_id'] = var['sourceInfo']['siteCode'][0]['value']
        #print(var['sourceInfo']['geoLocation'])
        df_temp['lat'] = var['sourceInfo']['geoLocation']['geogLocation']['latitude']
        df_temp['long'] = var['sourceInfo']['geoLocation']['geogLocation']['longitude']
        df_list.append(df_temp)
        df_temp.to_csv(path)
        #print(df)
    #df = pd.concat(df_list)

    #discretize_huc_response(json_obj)

    return df_list


def clean_data(df, column_change={'Streamflow, ft&#179;/s':'discharge_cfs'}, keep_nan = False, timestamp_col = 'dateTime', no_data=-999999):
    '''General house keeping on data: finding missing values and assign nan (if wanted) and changing the default column name. It also sets the timestamp column as index
    Inputs:
    - df: dataframe with the data from the REST API, generally with discharge
    - column_change: dictionary with the old (keys) column names and the new column name (value)
    - keep_nan: a boolean in case the nan values want to be kept
    - timestamp_col: the name of the column with the timestamp. Set to default-->dateTime
    - no_data: the json object from REST contains a no data number that can be used instead of assuming -999999. The default is -999999.
    Outputs:
    - df = return the same dataframe with the changes'''
    
    # Rename the default column name
    df.rename(columns=column_change, inplace = True)
    
    # Remove index column
# Change data types from "object" to their corresopnding type
    df = df.astype({list(column_change.values())[0]: float})
    df['dateTime']= pd.to_datetime(df['dateTime'])
    
    # Set nan values
    # TODO: get the no data value from the json object --> ['value']['timeSeries'][noDataValue][index][variable]
    df.replace(no_data, np.nan, inplace=True)
    if keep_nan:
        pass
    else:
        df.dropna(inplace=True)
    
    df[timestamp_col] = pd.to_datetime(df[timestamp_col], utc=True)   
    df.set_index(timestamp_col,inplace=True)

    return df


#def define_date_range(year):
#    return None


if __name__ == "__main__":
    query = {}
    query['id'] = '13060000'
    query['start_date'] = '2020-02-01'
    query['end_date'] = '2020-02-06'

    get_data(query)
    #lines = format_api_response(f"{query['site_no']}_{query['start_date']}_{query['end_date']}.txt")
    #print(lines[0])
