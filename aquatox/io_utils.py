# aquatox/io_utils.py
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import json
import re
from typing import Dict, List, Optional, Tuple

from .core import Environment
from .state import (
    StateVariable, Nutrient, Detritus, Plant, Animal, Biota,
    Oxygen, CarbonDioxide, Nitrate, Phosphorus, Toxicant,
)

# ObjID → Python-luokka -kartta
# Huom: 1006=TToxics (liuennut toksikantti), 1028=Detritus (sedimenttidetritus)
OBJID_MAP: Dict[int, str] = {
    1001: "Animal",
    1002: "Plant",
    1006: "Toxicant",       # TToxics — dissolved toxicant (PCBs, TCE, etc.)
    1013: "StateVariable",  # Temperature — env variable, skip
    1021: "Nitrate",
    1022: "Nutrient",       # TNH4Obj — ammonia
    1025: "Phosphorus",
    1026: "CarbonDioxide",
    1027: "Oxygen",
    1028: "Detritus",       # sediment detritus (corrected from recipe draft)
    1039: "Volume",         # TVolume — handled in Environment, skip
}


@dataclass
class LoadingRecord:
    use_constant: bool = False
    const_load: float = 0.0
    time_series: Dict[datetime, float] = field(default_factory=dict)
    alt_use_constant: bool = False
    alt_const_load: float = 0.0
    alt_time_series: Dict[datetime, float] = field(default_factory=dict)


class ScenarioIO:
    @staticmethod
    def load_initial_conditions(file: str) -> tuple[Environment, list[StateVariable]]:
        """Load a scenario file or fall back to a tiny synthetic scenario."""
        path = Path(file)
        if not path.exists():
            return ScenarioIO._load_synthetic()

        text = path.read_text(encoding="utf-8", errors="ignore")
        env = ScenarioIO._parse_environment(text)
        state_vars = ScenarioIO._parse_state_variables(text)
        if not state_vars:
            state_vars = ScenarioIO._default_state_vars()
        return env, state_vars

    @staticmethod
    def _load_synthetic() -> tuple[Environment, list[StateVariable]]:
        t0 = datetime(1992, 1, 1)
        inflow_series = {t0 + timedelta(days=i): 10.0 for i in range(10)}
        outflow_series = {t0 + timedelta(days=i): 10.0 for i in range(10)}
        env = Environment(
            volume=1_000.0,
            area=1_000.0,
            depth_mean=5.4,
            depth_max=25.0,
            inflow_series=inflow_series,
            outflow_series=outflow_series,
        )
        return env, ScenarioIO._default_state_vars()

    @staticmethod
    def _default_state_vars() -> list[StateVariable]:
        nitrate = Nutrient(name="Nitrate", value=0.4, units="mg/L", form="NO3")
        return [nitrate]

    @staticmethod
    def _parse_environment(text: str) -> Environment:
        volume = ScenarioIO._find_float(text, r'"StaticVolume":\s*([-\d.E+]+)') or 1_000.0
        area = ScenarioIO._find_float(text, r'"SurfArea":\s*([-\d.E+]+)') or 1_000.0
        depth_mean = ScenarioIO._find_float(text, r'"ICZMean":\s*([-\d.E+]+)') or 5.4
        depth_max = ScenarioIO._find_float(text, r'"ZMax":\s*([-\d.E+]+)') or 25.0

        inflow_series = ScenarioIO._parse_inflow_series(text)
        if inflow_series:
            mean_inflow = sum(inflow_series.values()) / len(inflow_series)
            outflow_series = {t: mean_inflow for t in inflow_series}
        else:
            t0 = datetime(1992, 1, 1)
            inflow_series = {t0 + timedelta(days=i): 0.0 for i in range(10)}
            outflow_series = {t0 + timedelta(days=i): 0.0 for i in range(10)}

        return Environment(
            volume=volume,
            area=area,
            depth_mean=depth_mean,
            depth_max=depth_max,
            inflow_series=inflow_series,
            outflow_series=outflow_series,
        )

    @staticmethod
    def _parse_inflow_series(text: str) -> Dict[datetime, float]:
        for item in ScenarioIO._extract_state_blocks(text):
            block = item["block"]
            if ScenarioIO._find_str(block, r'"PName\^":\s*"([^"]+)"') != "Water Volume":
                continue
            series_line = ScenarioIO._find_str(
                block, r"Alt\. Time Series Loadings:\s*n=\d+;([^\n]+)"
            )
            if not series_line:
                continue
            return ScenarioIO._parse_time_series(series_line)
        return {}

    @staticmethod
    def _parse_state_variables(text: str) -> list[StateVariable]:
        state_vars: list[StateVariable] = []
        for record in ScenarioIO._parse_state_records(text):
            sv = ScenarioIO._make_state_var(record)
            if sv is not None:
                state_vars.append(sv)
        return state_vars

    @staticmethod
    def _make_state_var(record: dict) -> Optional[StateVariable]:
        name = record["name"]
        value = record["initial"]
        units = record.get("units") or "arb"
        objid = record.get("objid")

        cls_name = OBJID_MAP.get(objid) if objid is not None else None

        # Skip environment-only variables
        if cls_name in ("Volume", "StateVariable"):
            return None

        if cls_name == "Nitrate":
            return Nitrate(name=name, value=value, units=units)
        if cls_name == "Phosphorus":
            return Phosphorus(
                name=name, value=value, units=units,
                frac_avail=record.get("frac_avail", 1.0),
                use_total_p=record.get("use_total_p", False),
            )
        if cls_name == "Oxygen":
            return Oxygen(name=name, value=value, units=units,
                          threshold=record.get("threshold", 3.0))
        if cls_name == "CarbonDioxide":
            return CarbonDioxide(name=name, value=value, units=units)
        if cls_name == "Toxicant":
            return Toxicant(name=name, value=value, units=units,
                            ppb=record.get("ppb", 0.0),
                            carrier_nstate=record.get("carrier_nstate", -1))
        if cls_name == "Detritus":
            lower = name.lower()
            return Detritus(name=name, value=value, units=units,
                            type="refractory" if "refrac" in lower else "labile",
                            layer="sediment" if "sed" in lower else "water")
        if cls_name == "Plant":
            return Plant(name=name, value=value, units=units, biomass=value,
                         max_growth=0.0, mortality_rate=0.0, nutrient_uptake_rate=0.0)
        if cls_name == "Animal":
            return Animal(name=name, value=value, units=units, biomass=value,
                          max_growth=0.0, mortality_rate=0.0,
                          feeding_prefs={}, consumption_rate=0.0)
        if cls_name == "Nutrient":
            lower = name.lower()
            form = "NH4" if ("ammonia" in lower or "nh4" in lower) else "?"
            return Nutrient(name=name, value=value, units=units, form=form)

        # Fallback: name-based heuristics for unknown ObjIDs
        lower = name.lower()
        if "nitrate" in lower or "no3" in lower:
            return Nitrate(name=name, value=value, units=units)
        if "ammonia" in lower or "nh4" in lower:
            return Nutrient(name=name, value=value, units=units, form="NH4")
        if "phosph" in lower or "po4" in lower:
            return Phosphorus(name=name, value=value, units=units)
        if "oxygen" in lower or " o2" in lower:
            return Oxygen(name=name, value=value, units=units)
        if "co2" in lower or "carbon dioxide" in lower:
            return CarbonDioxide(name=name, value=value, units=units)
        if "detritus" in lower:
            return Detritus(name=name, value=value, units=units,
                            type="refractory" if "refrac" in lower else "labile",
                            layer="sediment" if "sed" in lower else "water")
        if "tox" in lower or "pcb" in lower or "tce" in lower:
            return Toxicant(name=name, value=value, units=units)
        if ScenarioIO._looks_like_plant(lower):
            return Plant(name=name, value=value, units=units, biomass=value,
                         max_growth=0.0, mortality_rate=0.0, nutrient_uptake_rate=0.0)
        if ScenarioIO._looks_like_animal(lower):
            return Animal(name=name, value=value, units=units, biomass=value,
                          max_growth=0.0, mortality_rate=0.0,
                          feeding_prefs={}, consumption_rate=0.0)
        return StateVariable(name=name, value=value, units=units)

    @staticmethod
    def _looks_like_plant(name: str) -> bool:
        return any(token in name for token in ("diatoms", "greens", "cyanobacteria", "otheralg"))

    @staticmethod
    def _looks_like_animal(name: str) -> bool:
        return any(token in name for token in ("feeder", "fish", "zooplank", "chironomid", "oligochaete"))

    @staticmethod
    def _parse_state_records(text: str) -> list[dict]:
        records: list[dict] = []
        for item in ScenarioIO._extract_state_blocks(text):
            block = item["block"]
            name = ScenarioIO._find_str(block, r'"PName\^":\s*"([^"]+)"')
            if not name:
                continue
            value = ScenarioIO._find_float(block, r'"InitialCond":\s*([-\d.E+]+)')
            if value is None:
                continue
            units = ScenarioIO._find_str(block, r'"StateUnit":\s*"([^"]+)"') or "arb"

            record: dict = {
                "name": name,
                "initial": value,
                "units": units,
                "objid": item.get("objid"),
                "wrapper": item.get("wrapper"),
            }

            # Phosphorus extras
            frac = ScenarioIO._find_float(block, r'"FracAvail":\s*([-\d.E+]+)')
            if frac is not None:
                record["frac_avail"] = frac
            use_tp = ScenarioIO._find_str(block, r'"TP_IC":\s*(TRUE|FALSE)')
            if use_tp:
                record["use_total_p"] = use_tp.upper() == "TRUE"

            # Oxygen threshold
            threshold = ScenarioIO._find_float(block, r'"Threshhold":\s*([-\d.E+]+)')
            if threshold is not None:
                record["threshold"] = threshold

            # Toxicant extras
            ppb = ScenarioIO._find_float(block, r'"ppb":\s*([-\d.E+]+)')
            if ppb is not None:
                record["ppb"] = ppb
            carrier = ScenarioIO._find_float(block, r'"Carrier":\s*([-\d.E+]+)')
            if carrier is not None:
                record["carrier_nstate"] = int(carrier)

            # LoadingRecord
            loading = LoadingRecord()
            use_const = ScenarioIO._find_str(block, r'"UseConstant":\s*(TRUE|FALSE)')
            if use_const:
                loading.use_constant = use_const.upper() == "TRUE"
            const_load = ScenarioIO._find_float(block, r'"ConstLoad":\s*([-\d.E+]+)')
            if const_load is not None:
                loading.const_load = const_load
            ts = ScenarioIO._find_str(block, r'(?<!\. )Time Series Loadings:\s*n=\d+;([^\n]+)')
            if ts:
                loading.time_series = ScenarioIO._parse_time_series(ts)
            alt_use = ScenarioIO._find_str(block, r'"Alt_UseConstant":\s*(TRUE|FALSE)')
            if alt_use:
                loading.alt_use_constant = alt_use.upper() == "TRUE"
            alt_load = ScenarioIO._find_float(block, r'"Alt_ConstLoad":\s*([-\d.E+]+)')
            if alt_load is not None:
                loading.alt_const_load = alt_load
            alt_ts = ScenarioIO._find_str(block, r'Alt\. Time Series Loadings:\s*n=\d+;([^\n]+)')
            if alt_ts:
                loading.alt_time_series = ScenarioIO._parse_time_series(alt_ts)
            record["loading"] = loading

            records.append(record)
        return records

    @staticmethod
    def _extract_state_blocks(text: str) -> list[dict]:
        """Return {block, objid, wrapper} for each TStateVariable block."""
        blocks: list[dict] = []
        lines = text.splitlines()
        in_block = False
        depth = 0
        buffer: list[str] = []
        current_objid: Optional[int] = None
        current_wrapper: Optional[str] = None

        for line in lines:
            if not in_block:
                m = re.search(r'"ObjID":\s*(\d+)', line)
                if m:
                    current_objid = int(m.group(1))
                wm = re.match(r'\s*"(T\w+)":\s*\{', line)
                if wm and wm.group(1) != "TStateVariable":
                    current_wrapper = wm.group(1)

            if not in_block and '"TStateVariable": {' in line:
                in_block = True
                depth = 0
                buffer = [line]
                depth += line.count("{") - line.count("}")
                continue

            if in_block:
                buffer.append(line)
                depth += line.count("{") - line.count("}")
                if depth <= 0:
                    blocks.append({
                        "block": "\n".join(buffer),
                        "objid": current_objid,
                        "wrapper": current_wrapper,
                    })
                    in_block = False
                    current_objid = None
                    current_wrapper = None

        return blocks

    @staticmethod
    def _parse_time_series(series_blob: str) -> Dict[datetime, float]:
        entries = [seg.strip() for seg in series_blob.split(";") if seg.strip()]
        series: Dict[datetime, float] = {}
        for entry in entries:
            if "," not in entry:
                continue
            date_text, value_text = entry.split(",", 1)
            date_text = date_text.strip()
            value_text = value_text.strip()
            for fmt in ("%d.%m.%Y", "%d/%m/%Y"):
                try:
                    series[datetime.strptime(date_text, fmt)] = float(value_text)
                    break
                except ValueError:
                    continue
        return series

    @staticmethod
    def _find_float(text: str, pattern: str) -> Optional[float]:
        match = re.search(pattern, text)
        if not match:
            return None
        try:
            return float(match.group(1))
        except ValueError:
            return None

    @staticmethod
    def _find_str(text: str, pattern: str) -> Optional[str]:
        match = re.search(pattern, text)
        if not match:
            return None
        return match.group(1)

    @staticmethod
    def export_state_variables(file: str, json_path: str, csv_path: str) -> list[dict]:
        path = Path(file)
        text = path.read_text(encoding="utf-8", errors="ignore")
        records = ScenarioIO._parse_state_records(text)
        mapping = []
        for record in records:
            obj = ScenarioIO._make_state_var(record)
            mapping.append({
                "name": record["name"],
                "initial": record["initial"],
                "units": record.get("units"),
                "mapped_class": obj.__class__.__name__ if obj else "skipped",
            })
        json_out = Path(json_path)
        json_out.parent.mkdir(parents=True, exist_ok=True)
        json_out.write_text(json.dumps(mapping, indent=2), encoding="utf-8")
        csv_out = Path(csv_path)
        csv_out.parent.mkdir(parents=True, exist_ok=True)
        with csv_out.open("w", encoding="utf-8", newline="") as handle:
            import csv
            writer = csv.DictWriter(handle, fieldnames=["name", "initial", "units", "mapped_class"])
            writer.writeheader()
            writer.writerows(mapping)
        return mapping

    @staticmethod
    def load_forcing(file: str) -> dict:
        return {}

    @staticmethod
    def save_output(results, file: str) -> None:
        if not results:
            return
        import csv
        times, first = results[0]
        names = sorted(first.keys())
        with open(file, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["time"] + names)
            for t, snapshot in results:
                w.writerow([t.isoformat()] + [snapshot.get(n, "") for n in names])


class Utils:
    @staticmethod
    def interpolate_series(series, t):
        return series.get(t, 0.0)

    @staticmethod
    def calc_light_penetration():
        return 1.0
