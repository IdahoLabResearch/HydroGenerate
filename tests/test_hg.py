from HydroGenerate.utils.api_call import *
from HydroGenerate.hydropower_potential import *


# test basic hydropower calculation
def test_calculate_potential():
    flow = 8000 # given flow, in cfs
    head = 20 # head, in ft
    power = None

    hp = calculate_hp_potential(flow= flow, head= head, rated_power= power, system_efficiency= 0.7)

    assert round(hp.rated_power, 0) == 9483


# test diversion mode
def test_diversion_calculate_potential():

    flow_data = {'dateTime': pd.Series(['2010-01-01 08:00:00+00:00', '2010-01-01 08:15:00+00:00',
                                    '2010-01-01 08:30:00+00:00', '2010-01-01 08:45:00+00:00',
                                    '2010-01-01 09:00:00+00:00', '2010-01-01 09:15:00+00:00',
                                    '2010-01-01 09:30:00+00:00', '2010-01-01 09:45:00+00:00',
                                    '2010-01-01 10:00:00+00:00', '2010-01-01 10:15:00+00:00']),
            'discharge_cfs': pd.Series([3260, 3270, 3250, 3270, 3310, 3290, 3300,
                                        3300, 3330, 3260])}

    flow = pd.DataFrame(flow_data)
    flow['dateTime'] = pd.to_datetime(flow['dateTime']) # preprocessing convert to datetime
    flow = flow.set_index('dateTime') # set datetime index # flolw is in cfs

    head = 20 # ft
    power = None
    penstock_length = 50 # ft
    hp_type = 'Diversion' 

    hp = calculate_hp_potential(flow= flow, rated_power= power, head= head,
                                pctime_runfull = 30,
                                penstock_headloss_calculation= True,
                                design_flow= None,
                                electricity_sell_price = 0.05,
                                resource_category= 'CanalConduit',
                                hydropower_type= hp_type, penstock_length= penstock_length,
                                flow_column= 'discharge_cfs', annual_caclulation= True)
    assert round(hp.rated_power, 0) == 4505


