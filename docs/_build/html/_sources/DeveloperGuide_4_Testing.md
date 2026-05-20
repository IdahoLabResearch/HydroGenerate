# HydroGenerate Test Suite

This page documents the purpose and coverage of the automated tests for **HydroGenerate**, located in `tests/test_hg.py`.

You can run all tests locally or in CI with:

```bash
pytest -q
```

---

## 1. Basic Hydropower Tests

- **`test_basic_hydropower_calculation`**  
  Confirms that the `calculate_hp_potential()` function produces the correct rated power for a simple BASIC hydropower configuration.

- **`test_units_roundtrip_basic`**  
  Ensures hydropower results remain consistent when switching between **US** and **SI** units.

---

## 2. Diversion Projects

- **`test_diversion_calculate_potential`**  
  Runs an end-to-end diversion test using a short flow DataFrame, verifying that power, design flow, and revenue are computed correctly.

- **`test_diversion_`**  
  Ensures turbine efficiency values remain between 0 and 1, and headloss is computed correctly.

- **`test_percent_exceedance_design_flow_uses_P70_when_pe_30`**  
  Verifies that a percent exceedance of 30 selects the 70th percentile of flow as the design flow.

- **`test_min_turbineflow_default_10_percent_clamps_to_zero`**  
  Confirms that the minimum turbine flow defaults to 10% of the design flow and that smaller flows are clamped to zero.

---

## 3. Headloss Models

- **`test_headloss_methods_run`**  
  Ensures both **Darcy–Weisbach** and **Hazen–Williams** methods run successfully.

- **`test_darcy_headloss_increases_with_length_si`**  
  Verifies that longer penstock lengths produce higher headloss and lower rated power.

- **`test_hazen_williams_infers_diameter_when_missing`**  
  Checks that Hazen–Williams can infer penstock diameter when not provided.

---

## 4. Turbine Selection & Efficiency

- **`test_turbine_type_selector_inside_regions`**  
  Confirms correct turbine type (Kaplan, Francis, Turgo, Crossflow) is chosen for valid flow–head pairs.

- **`test_generator_efficiency_default_applied`**  
  Ensures the default generator efficiency (0.98) is applied and a valid runner diameter is assigned.

---

## 5. Hydrokinetic Projects

- **`test_hydrokinetic_mode_simple_si`**  
  Verifies that hydrokinetic power > 0 when blade area and velocity are given and that costs are skipped.

---

## 6. Economic Calculations

- **`test_costs_present_for_diversion_canalconduit_us`**  
  Checks that the ORNL Baseline Cost Model sets **ICC** (initial capital cost) and **annual O&M** for canal conduit projects.

- **`test_costs_present_for_diversion_npd_alias`**  
  Verifies that the “NPD” alias for non-powered dams produces valid cost outputs.

- **`test_annual_om_is_capped_at_2p5_percent_of_icc_when_applicable`**  
  Confirms that annual O&M ≤ 2.5% of ICC, per model guidance.

- **`test_costs_not_computed_for_hydrokinetic`**  
  Ensures hydrokinetic projects skip cost modeling.

---

## 7. Revenue Calculations

- **`test_revenue_capacity_factor_path_sets_days_and_energy`**  
  Checks that providing a capacity factor sets the correct number of operation days and computes annual energy correctly.

- **`test_revenue_days_path_sets_capacity_factor_and_energy`**  
  Validates the reverse case: providing days sets the capacity factor and energy outputs correctly.

- **`test_revenue_outputs_present_and_valid`**  
  Ensures DataFrame-based revenue calculations produce valid, non-negative energy and revenue values.

- **`test_revenue_dataframe_path_uses_default_price_when_none`**  
  Verifies that default wholesale electricity price (0.0582 $/kWh) is applied when none is provided.

- **`test_dataframe_revenue_groupby_yields_reasonable_capacity_factor`**  
  Confirms that the computed capacity factor is clamped between 0 and 1.

---

## 8. Error Handling

- **`test_missing_flow_column_raises`**  
  Ensures a missing `flow_column` parameter raises a `ValueError`.

- **`test_invalid_units_raise`**  
  Confirms invalid unit strings raise an error.

- **`test_invalid_hydropower_type_raises`**  
  Ensures unsupported hydropower types are rejected.

- **`test_diversion_requires_penstock_length_when_headloss_calc_true`**  
  Verifies that penstock length is required if headloss calculation is enabled.

---

## 9. Conventions and Notes

- All DataFrames use a `dateTime` index.  
- Frequency codes use lowercase (`"h"`) to avoid pandas deprecation warnings.  
- Floating-point comparisons use `pytest.approx()` for stability.  
- Run the tests regularly to ensure physics, units, and economics remain consistent.

---

## Running Tests

From the repository root:

```bash
pip install -e HydroGenerate
pip install pytest
pytest -q
```

