# tests/test_stage1.py
import math
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from aquatox.core import Simulation, ODESolver, Environment
from aquatox.state import StateVariable, Nutrient, Biota, Oxygen, Phosphorus, Toxicant
from aquatox.io_utils import ScenarioIO, OBJID_MAP

DATA_DIR = Path(__file__).parent.parent

# ---- Helpers ----
class ConstantRateVar(StateVariable):
    def rate(self, t, dt, env, state_vars):
        return self._c

    def __init__(self, name, value, units, c):
        super().__init__(name=name, value=value, units=units)
        self._c = c

def _mk_env_with_flows(v0=1000.0, inflow=10.0, outflow=5.0, days=2):
    t0 = datetime(1992,1,1)
    inflow_series = {t0 + timedelta(days=i): inflow for i in range(days+1)}
    outflow_series = {t0 + timedelta(days=i): outflow for i in range(days+1)}
    return Environment(
        volume=v0, area=1000.0, depth_mean=5.4, depth_max=25.0,
        inflow_series=inflow_series, outflow_series=outflow_series
    ), t0

# ---- Stage-1 tests ----
def test_euler_integrator_constant_rate_step():
    env, t0 = _mk_env_with_flows()
    x = ConstantRateVar(name="X", value=0.0, units="arb", c=5.0)  # dX/dt = 5
    sim = Simulation(env=env, state_vars=[x], solver=ODESolver(method="Euler"))
    sim.solver.integrate(sim.state_vars, env, t0, dt_days=1.0)
    assert x.value == pytest.approx(5.0)

def test_environment_water_balance_updates_volume():
    env, t0 = _mk_env_with_flows(v0=1000.0, inflow=10.0, outflow=5.0, days=1)
    x = ConstantRateVar(name="X", value=0.0, units="arb", c=0.0)
    sim = Simulation(env=env, state_vars=[x], solver=ODESolver(method="Euler"))
    sim.run(time_end=t0 + timedelta(days=1), dt_days=1.0)
    # Volume = 1000 + (10-5)*1day = 1005
    assert sim.env.volume == pytest.approx(1005.0)

def test_scenarioio_minimal_load_and_run_stable():
    sim = Simulation.load_scenario("dummy-path")
    # run two days
    end = min(sim.env.inflow_series.keys()) + timedelta(days=2)
    sim.run(time_end=end, dt_days=1.0)
    out = sim.output_results()
    assert len(out) >= 2
    # Nitrate is inert in Stage-1 -> unchanged
    nitrates = [frame["Nitrate"] for _, frame in out]
    assert all(v == pytest.approx(0.4) for v in nitrates)

def test_biota_growth_minus_mortality():
    env, t0 = _mk_env_with_flows()
    b = Biota(name="TestBiota", value=1.0, units="mg/L", biomass=1.0, max_growth=0.2, mortality_rate=0.1)
    sim = Simulation(env=env, state_vars=[b], solver=ODESolver(method="Euler"))
    sim.solver.integrate(sim.state_vars, env, t0, dt_days=1.0)
    # Net rate = (0.2 - 0.1)*1.0 = 0.1 -> value should be 1.1
    assert b.value == pytest.approx(1.1, rel=1e-6)

# ---- Stage-2 parser tests ----
def test_pyhajarvi_nutrients_parsed():
    """Pyhäjärvi: Phosphorus and Oxygen are recognised from ObjID."""
    _, svars = ScenarioIO.load_initial_conditions(str(DATA_DIR / "LakePyhajarviFinland.txt"))
    classes = {type(sv).__name__ for sv in svars}
    assert "Phosphorus" in classes, f"Phosphorus missing, got: {classes}"
    assert "Oxygen" in classes, f"Oxygen missing, got: {classes}"

def test_ontario_toxicants_parsed():
    """Lake Ontario PCBs: TToxics objects (ObjID 1006) are parsed as Toxicant."""
    _, svars = ScenarioIO.load_initial_conditions(str(DATA_DIR / "Lake Ontario PCBs.txt"))
    toxicants = [sv for sv in svars if isinstance(sv, Toxicant)]
    assert len(toxicants) > 0, "No Toxicant instances found in Ontario scenario"
    # Spot-check: first one should be a dissolved PCB
    assert "PCB" in toxicants[0].name or "tox" in toxicants[0].name.lower()

def test_objid_classification():
    """OBJID_MAP: ObjID 1027 → Oxygen, 1025 → Phosphorus, 1006 → Toxicant."""
    cases = [
        ({"name": "Dissolved Oxygen", "initial": 8.0, "units": "mg/L", "objid": 1027}, Oxygen),
        ({"name": "Total P", "initial": 0.05, "units": "mg/L", "objid": 1025}, Phosphorus),
        ({"name": "Dissolved org. tox 1: [PCB 18]", "initial": 0.0, "units": "ppb", "objid": 1006}, Toxicant),
    ]
    for record, expected_cls in cases:
        sv = ScenarioIO._make_state_var(record)
        assert isinstance(sv, expected_cls), (
            f"ObjID {record['objid']}: expected {expected_cls.__name__}, got {type(sv).__name__}"
        )
