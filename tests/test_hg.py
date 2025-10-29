# from HydroGenerate.utils.api_call import *
import pandas as pd
import pytest
import numpy as np
from HydroGenerate.hydropower_potential import calculate_hp_potential
from HydroGenerate.turbine_calculation import (TurbineParameters,
                                               turbine_type_selector,
                                               FrancisTurbine,
                                               TurgoTurbine,
                                               PeltonTurbine)


# ---------- FIXTURE ----------
@pytest.fixture
def short_flow_df():
    """Short time-series DataFrame for Diversion tests."""
    rng = pd.date_range("2010-01-01", periods=4 * 24 * 40, freq="15min", tz="UTC")
    flow = 3000 + 200 * np.sin(np.linspace(0, 20 * np.pi, len(rng)))
    df = pd.DataFrame({"discharge_cfs": flow}, index=rng)
    df.index.name = "dateTime"
    return df

# ---------- BASIC HYDROPOWER ----------
def test_basic_hydropower_calculation():
    """Check Basic mode computes correct rated power."""
    hp = calculate_hp_potential(flow=8000, head=20, rated_power=None, system_efficiency=0.7)
    assert hp.rated_power == pytest.approx(9483, abs=1)

# ---------- DIVERSION MODE ----------
def test_diversion_calculate_potential():
    """Diversion mode: FDC-based design flow, headloss calc, revenue on DF input."""

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



# ---------- DIVERSION MODE ----------
def test_diversion_(short_flow_df):
    """Diversion mode asserting head loss, turbine efficiency"""
    hp = calculate_hp_potential(
        flow=short_flow_df,
        flow_column="discharge_cfs",
        head=20,
        units="US",
        hydropower_type="Diversion",
        penstock_headloss_calculation=True,
        penstock_headloss_method="Darcy-Weisbach",
        penstock_length=50,
        pctime_runfull=30,
        annual_caclulation=True,
        electricity_sell_price=0.05,
        resource_category="CanalConduit",
    )
    assert hp.rated_power > 0
    assert (hp.turbine_efficiency >= 0).all() and (hp.turbine_efficiency <= 1).all()
    assert hp.head_loss is not None

# ---------- UNITS ROUND-TRIP ----------
def test_units_roundtrip_basic():
    """US vs SI unit consistency."""
    hp_us = calculate_hp_potential(flow=8000, head=20, units="US", system_efficiency=0.7)
    hp_si = calculate_hp_potential(flow=8000 * 0.0283168, head=20 * 0.3048, units="SI", system_efficiency=0.7)
    assert hp_us.rated_power == pytest.approx(hp_si.rated_power, rel=1e-3)

# ---------- HEADLOSS METHODS ----------
@pytest.mark.parametrize("method", ["Darcy-Weisbach", "Hazen-Williams"])
def test_headloss_methods_run(method):
    """Both headloss methods execute successfully."""
    hp = calculate_hp_potential(
        flow=6000,
        head=30,
        units="US",
        hydropower_type="Diversion",
        penstock_headloss_calculation=True,
        penstock_headloss_method=method,
        penstock_length=100,
    )
    assert hp.head_loss is not None


# ---------- TURBINE SELECTION ----------
@pytest.mark.parametrize(
    "design_flow, head, expected",
    [
        (5, 150, "Turgo"),
        (20, 80, "Francis"),
        (1.5, 8, "Crossflow")
    ],
)
def test_turbine_type_selector_inside_regions(design_flow, head, expected):
    """Ensure turbine selector chooses expected turbine for valid (flow, head) points."""
    t = TurbineParameters(
        turbine_type=None,
        flow=design_flow,
        design_flow=design_flow,
        flow_column=None,
        head=head,
        rated_power=None,
        system_efficiency=None,
        generator_efficiency=None,
        Rm=None,
        pctime_runfull=None,
        pelton_n_jets=None,
        hk_blade_diameter=None,
        hk_blade_heigth=None,
        hk_blade_type=None,
        hk_swept_area=None,
    )
    turbine_type_selector(t)
    assert t.turbine_type.lower() == expected.lower()

# ---------- ERRORS ----------
def test_missing_flow_column_raises(short_flow_df):
    """Raises ValueError if DataFrame flow_column not provided."""
    with pytest.raises(ValueError):
        calculate_hp_potential(flow=short_flow_df, head=10, hydropower_type="Diversion")


def test_invalid_units_raise():
    """Raises ValueError for unsupported units."""
    with pytest.raises(ValueError):
        calculate_hp_potential(flow=1000, head=10, units="METRIC")



