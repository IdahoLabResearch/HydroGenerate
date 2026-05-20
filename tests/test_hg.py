# from HydroGenerate.utils.api_call import *
import pandas as pd
import pytest
import numpy as np
from HydroGenerate.hydropower_potential import calculate_hp_potential, calculate_head
from HydroGenerate.turbine_calculation import (TurbineParameters,
                                               turbine_type_selector,
                                               FrancisTurbine,
                                               TurgoTurbine,
                                               PeltonTurbine)
from HydroGenerate.flow_preprocessing import FlowPreProcessing


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



def _df_from(vals, freq="h"): 
    idx = pd.date_range("2012-05-01 00:00:00", periods=len(vals), freq=freq, tz="UTC")
    df = pd.DataFrame({"discharge_cfs": vals}, index=idx)
    df.index.name = "dateTime"
    return df



def test_percent_exceedance_design_flow_uses_P70_when_pe_30():
    """With pe=30, PercentExceedance selects the 70th percentile of the flow series."""
    vals = np.array([1000, 1200, 1500, 1800, 2000, 2200, 2500, 3000, 3500, 4000], dtype=float)
    df = _df_from(vals, freq="h")
    hp = calculate_hp_potential(
        flow=df, head=50, units="US", hydropower_type="Diversion",
        flow_column="discharge_cfs", pctime_runfull=30,  # 30% => design flow = P70
        penstock_headloss_calculation=False
    )
    expected_p70 = np.percentile(vals, 70)
    assert hp.design_flow == pytest.approx(expected_p70, rel=1e-6)

def test_min_turbineflow_default_10_percent_clamps_to_zero():
    """When min flow not provided, default = 10% of design; flows below clamp to zero."""
    class Obj: pass
    o = Obj()
    o.flow = np.array([2.0, 8.0, 10.0, 15.0, 25.0])  # cfs
    o.design_flow = 100.0
    o.minimum_turbineflow = None
    o.minimum_turbineflow_percent = None
    FlowPreProcessing().max_turbineflow_checker(o)   # creates turbine_flow
    FlowPreProcessing().min_turbineflow_checker(o)   # apply min clamp
    assert np.array_equal(o.turbine_flow, np.array([0.0, 0.0, 10.0, 15.0, 25.0]))

def test_darcy_headloss_increases_with_length_si():
    """Longer penstock length => larger headloss => lower rated power (SI)."""
    hp_short = calculate_hp_potential(
        flow=1.5, head=60.0, units="SI", hydropower_type="Diversion",
        penstock_headloss_calculation=True, penstock_headloss_method="Darcy-Weisbach",
        penstock_length=50.0, penstock_material="Steel",
        design_flow=1.5, pctime_runfull=30
    )
    hp_long = calculate_hp_potential(
        flow=1.5, head=60.0, units="SI", hydropower_type="Diversion",
        penstock_headloss_calculation=True, penstock_headloss_method="Darcy-Weisbach",
        penstock_length=150.0, penstock_material="Steel",
        design_flow=1.5, pctime_runfull=30
    )
    assert hp_long.rated_power < hp_short.rated_power

def test_hazen_williams_infers_diameter_when_missing():
    """HW method should compute diameter if not provided when max_headloss_allowed present."""
    hp = calculate_hp_potential(
        flow=1.25, head=50.0, units="SI", hydropower_type="Diversion",
        penstock_headloss_calculation=True, penstock_headloss_method="Hazen-Williams",
        penstock_length=120.0, penstock_material="Steel",
        penstock_diameter=None, max_headloss_allowed=8.0,
        design_flow=1.25, pctime_runfull=30
    )
    assert hp.penstock_diameter is not None and hp.penstock_design_headloss is not None
    assert hp.penstock_design_headloss > 0

def test_revenue_outputs_present_and_valid():
    """Revenue/DataFrame outputs exist and have sane values with hourly DF input."""
    flow = _df_from([3300 + 10*i for i in range(24)], freq="h")
    hp = calculate_hp_potential(
        flow=flow, head=25, units="US", hydropower_type="Diversion",
        flow_column="discharge_cfs", penstock_headloss_calculation=False,
        pctime_runfull=30, annual_caclulation=True, electricity_sell_price=0.05
    )
    assert hp.dataframe_output is not None
    assert hp.annual_dataframe_output is not None
    cf = hp.annual_dataframe_output["capacity_factor"]
    assert ((cf >= 0) & (cf <= 1)).all()
    assert (hp.annual_dataframe_output["revenue_M$"] >= 0).all()

def test_hydrokinetic_mode_simple_si():
    """Hydrokinetic: power > 0 when swept area & velocity provided."""
    hp = calculate_hp_potential(
        hydropower_type="Hydrokinetic", units="SI",
        channel_average_velocity=2.0,   # m/s
        hk_blade_diameter=2.0,          # m  => A = pi*D^2/4 ≈ 3.1416
        system_efficiency=None          # will default to Betz limit (59%)
    )
    assert hp.rated_power > 0

def test_generator_efficiency_default_applied(short_flow_df):
    """Generator efficiency defaults to 0.98 proportion in Diversion mode."""
    hp = calculate_hp_potential(
        flow=short_flow_df, head=20, units="US", hydropower_type="Diversion",
        flow_column="discharge_cfs", penstock_headloss_calculation=False,
        pctime_runfull=30
    )
    # In Diversion() code, default sets to 0.98 (already as proportion)
    assert hp.generator_efficiency == pytest.approx(0.98, rel=1e-9)

    # Depending on selection (Francis/Kaplan/Propeller), runner_diameter should be set (>0)
    assert getattr(hp, "runner_diameter", None) is not None
    assert hp.runner_diameter > 0

def test_invalid_hydropower_type_raises():
    """Unsupported hydropower type should raise."""
    with pytest.raises(ValueError):
        calculate_hp_potential(flow=1000, head=10, hydropower_type="BOGUS")

def test_diversion_requires_penstock_length_when_headloss_calc_true(short_flow_df):
    """Diversion + headloss calc without length should raise ValueError."""
    with pytest.raises(ValueError):
        calculate_hp_potential(
            flow=short_flow_df, head=20, units="US", hydropower_type="Diversion",
            flow_column="discharge_cfs",
            penstock_headloss_calculation=True,  # missing penstock_length -> raise
            pctime_runfull=30
        )



def _tiny_df(vals, freq="h"): 
    idx = pd.date_range("2017-01-01 00:00:00", periods=len(vals), freq=freq, tz="UTC")
    df = pd.DataFrame({"discharge_cfs": vals}, index=idx)
    df.index.name = "dateTime"
    return df


def test_costs_present_for_diversion_canalconduit_us():
    """Cost model should populate ICC and annual O&M for non-HK projects."""
    hp = calculate_hp_potential(
        flow=6000, head=30, units="US",
        hydropower_type="Diversion",
        penstock_headloss_calculation=True,
        penstock_headloss_method="Hazen-Williams",
        penstock_length=120,
        resource_category="CanalConduit",  # commonly used in your codebase
        design_flow=6000, pctime_runfull=30,
    )
    # The ORNL HBCM should set these:
    assert hasattr(hp, "icc") and hp.icc is not None and hp.icc > 0
    assert hasattr(hp, "annual_om") and hp.annual_om is not None and hp.annual_om > 0


def test_costs_present_for_diversion_npd_alias():
    """Alias category 'NPD' (non-powered dam) should be recognized and produce costs."""
    hp = calculate_hp_potential(
        flow=7000, head=40, units="US",
        hydropower_type="Diversion",
        penstock_headloss_calculation=False,
        resource_category="NPD",
        design_flow=7000, pctime_runfull=30,
    )
    assert hasattr(hp, "icc") and hp.icc > 0
    assert hasattr(hp, "annual_om") and hp.annual_om > 0


def test_annual_om_is_capped_at_2p5_percent_of_icc_when_applicable():
    """
    For all categories except 'GENERATORREWIND', annual O&M must satisfy:
      annual_om <= 0.025 * icc
    """
    hp = calculate_hp_potential(
        flow=5000, head=60, units="US",
        hydropower_type="Diversion",
        penstock_headloss_calculation=False,
        resource_category="CanalConduit",
        design_flow=5000, pctime_runfull=30,
    )
    assert hp.annual_om <= 0.025 * hp.icc + 1e-12  # small epsilon for float noise


def test_costs_not_computed_for_hydrokinetic():
    """Hydrokinetic path should skip ORNL HBCM cost calculation."""
    hk = calculate_hp_potential(
        hydropower_type="Hydrokinetic", units="SI",
        channel_average_velocity=2.0, hk_blade_diameter=2.0,
    )
    # By design, HK skips cost calculation:
    assert not hasattr(hk, "icc")
    assert not hasattr(hk, "annual_om")


def test_revenue_capacity_factor_path_sets_days_and_energy():
    """
    ConstantEletrictyPrice path (non-DataFrame) with capacity_factor provided:
      - n_operation_days should become capacity_factor*365
      - annual_energy_generated = capacity_factor * mean(power) * 24 * 365
    """
    hp = calculate_hp_potential(
        flow=4000, head=25, units="US",
        hydropower_type="Diversion",
        penstock_headloss_calculation=False,
        design_flow=4000, pctime_runfull=30,
        annual_caclulation=True,
        electricity_sell_price=0.10,
        capacity_factor=0.5,         # 50%
        n_operation_days=None,
    )
    # Derived days
    assert hp.n_operation_days == pytest.approx(0.5 * 365, rel=1e-12)

    # Reconstruct expected energy from outputs:
    # hp.power is a vector over generated flow range in Diversion mode
    mean_power = float(np.mean(hp.power))
    expected_kwh = 0.5 * mean_power * 24 * 365
    assert hp.annual_energy_generated == pytest.approx(expected_kwh, rel=1e-6)
    # Revenue should reflect price
    assert hp.annual_revenue == pytest.approx(hp.annual_energy_generated * 0.10 / 1e6, rel=1e-6)


def test_revenue_days_path_sets_capacity_factor_and_energy():
    """
    ConstantEletrictyPrice path (non-DataFrame) with n_operation_days provided:
      - capacity_factor = n_days * 100 / 365   (per code)
      - annual_energy_generated = n_days * mean(power) * 24
    """
    hp = calculate_hp_potential(
        flow=4500, head=22, units="US",
        hydropower_type="Diversion",
        penstock_headloss_calculation=False,
        design_flow=4500, pctime_runfull=30,
        annual_caclulation=True,
        electricity_sell_price=0.08,
        capacity_factor=None,
        n_operation_days=200,
    )
    # capacity_factor stored as *percentage* in this branch per code
    assert hp.capacity_factor == pytest.approx(200 * 100 / 365, rel=1e-12)

    mean_power = float(np.mean(hp.power))
    expected_kwh = 200 * mean_power * 24
    assert hp.annual_energy_generated == pytest.approx(expected_kwh, rel=1e-6)
    assert hp.annual_revenue == pytest.approx(hp.annual_energy_generated * 0.08 / 1e6, rel=1e-6)


def test_revenue_dataframe_path_uses_default_price_when_none():
    """
    ConstantEletrictyPrice_pd path should default to wholesale_elecprice_2023
    when electricity_sell_price is None.
    """
    flow = _tiny_df([3200 + i for i in range(48)], freq="h")
    hp = calculate_hp_potential(
        flow=flow, head=20, units="US",
        hydropower_type="Diversion",
        flow_column="discharge_cfs",
        penstock_headloss_calculation=False,
        annual_caclulation=True,
        electricity_sell_price=None,   # triggers default
        pctime_runfull=30,
    )
    # Default price wired in the module:
    assert hp.electricity_sell_price == pytest.approx(0.0582, rel=1e-12)
    # Annual outputs tables exist
    assert hp.dataframe_output is not None
    assert hp.annual_dataframe_output is not None
    # Basic sanity on totals
    assert (hp.annual_dataframe_output["total_annual_energy_KWh"] > 0).all()
    assert (hp.annual_dataframe_output["revenue_M$"] >= 0).all()


def test_dataframe_revenue_groupby_yields_reasonable_capacity_factor():
    """Capacity factor from time-series path must be clamped to [0, 1]."""
    flow = _tiny_df([5000] * (24 * 30), freq="h")  # one month of hourly data
    hp = calculate_hp_potential(
        flow=flow, head=30, units="US",
        hydropower_type="Diversion",
        flow_column="discharge_cfs",
        penstock_headloss_calculation=False,
        annual_caclulation=True,
        electricity_sell_price=0.06,
        pctime_runfull=30,
    )
    cf = hp.annual_dataframe_output["capacity_factor"]
    assert ((cf >= 0) & (cf <= 1)).all()

