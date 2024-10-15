from HydroGenerate.utils.api_call import *
from HydroGenerate.hydropower_potential import *
import pytest

def test_calculate_potential():
    flow = 8000 # given flow, in cfs
    head = 20 # head, in ft
    power = None

    hp = calculate_hp_potential(flow= flow, head= head, rated_power= power, system_efficiency= 0.7)

    assert round(hp.rated_power, 0) == 9483

