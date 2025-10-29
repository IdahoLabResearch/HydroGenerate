# Test file

# tests/test_hydrogenerate_fullsuite.py
"""
Comprehensive HydroGenerate test suite.

Covers:
- Basic, Diversion, and Hydrokinetic hydropower calculations
- Turbine selection and efficiency curves
- Unit conversions
- Headloss methods
- Revenue calculations
- Maintenance logic
- Error handling
"""

import numpy as np
import pandas as pd
import pytest

from HydroGenerate.hydropower_potential import calculate_hp_potential
from HydroGenerate.turbine_calculation import (
    TurbineParameters,
    turbine_type_selector,
    FrancisTurbine,
    TurgoTurbine,
    PeltonTurbine,
)


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
def test_diversion_full_pipeline_with_maintenance(short_flow_df):
    """Diversion mode full pipeline with maintenance and headloss."""
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
        annual_maintenance_flag=True,
        major_maintenance_flag=True,
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
        (5, 150, "Pelton"),
        (20, 80, "Francis"),
        (1.5, 8, "Kaplan"),
        (3, 60, "Turgo"),
        (2, 6, "Crossflow"),
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


# ---------- EFFICIENCY CURVES ----------
def _tp(Qd=10, H=50):
    """Helper to create TurbineParameters."""
    return TurbineParameters(
        turbine_type=None,
        flow=Qd,
        design_flow=Qd,
        flow_column=None,
        head=H,
        rated_power=None,
        system_efficiency=None,
        generator_efficiency=None,
        Rm=4.5,
        pctime_runfull=30,
        pelton_n_jets=3,
        hk_blade_diameter=None,
        hk_blade_heigth=None,
        hk_blade_type=None,
        hk_swept_area=None,
    )


def test_francis_efficiency_bounds_and_runner():
    """Francis turbine: efficiency in [0,1] and runner diameter positive."""
    t = _tp()
    FrancisTurbine().turbine_calculator(t)
    assert (t.turbine_efficiency >= 0).all() and (t.turbine_efficiency <= 1).all()
    assert t.runner_diameter and t.runner_diameter > 0


def test_turgo_approx_pelton_minus_0p03():
    """Turgo efficiency ≈ Pelton - 0.03 (bounded at zero)."""
    t1 = _tp(H=80)
    t2 = _tp(H=80)
    PeltonTurbine().turbine_calculator(t1)
    TurgoTurbine().turbine_calculator(t2)
    diff = t1.turbine_efficiency - t2.turbine_efficiency
    mask = t1.turbine_efficiency > 0.05
    assert np.allclose(diff[mask], 0.03, atol=0.01)


# ---------- REVENUE ----------
def test_constant_price_days_vs_cf_agree():
    """Revenue and energy identical when using days or capacity_factor."""
    idx = pd.date_range("2020-01-01", periods=24 * 30, freq="H", tz="UTC")
    flow = pd.DataFrame({"discharge_cfs": np.full(len(idx), 5000)}, index=idx)

    hp_days = calculate_hp_potential(
        flow=flow,
        flow_column="discharge_cfs",
        head=20,
        units="US",
        hydropower_type="Diversion",
        penstock_length=50,
        penstock_headloss_calculation=False,
        annual_caclulation=True,
        n_operation_days=200,
        electricity_sell_price=0.05,
    )
    hp_cf = calculate_hp_potential(
        flow=flow,
        flow_column="discharge_cfs",
        head=20,
        units="US",
        hydropower_type="Diversion",
        penstock_length=50,
        penstock_headloss_calculation=False,
        annual_caclulation=True,
        capacity_factor=200 / 365,
        electricity_sell_price=0.05,
    )

    assert hp_days.annual_energy_generated == pytest.approx(hp_cf.annual_energy_generated, rel=1e-6)
    assert hp_days.annual_revenue == pytest.approx(hp_cf.annual_revenue, rel=1e-6)


# ---------- ERRORS ----------
def test_missing_flow_column_raises(short_flow_df):
    """Raises ValueError if DataFrame flow_column not provided."""
    with pytest.raises(ValueError):
        calculate_hp_potential(flow=short_flow_df, head=10, hydropower_type="Diversion")


def test_invalid_units_raise():
    """Raises ValueError for unsupported units."""
    with pytest.raises(ValueError):
        calculate_hp_potential(flow=1000, head=10, units="METRIC")


def test_too_many_days_raises():
    """Raises ValueError if n_operation_days > 365."""
    with pytest.raises(ValueError):
        calculate_hp_potential(flow=1000, head=10, units="US", annual_caclulation=True, n_operation_days=400)
