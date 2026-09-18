# Resepti: Parserin laajennus — täysi tilamuuttujakirjasto

## Konteksti

Nykyinen `ScenarioIO._parse_state_records()` tunnistaa tilamuuttujat vain nimen perusteella
(`_looks_like_plant`, `_looks_like_animal`). Tavoite on tunnistaa kaikki AQUATOX-tyypit
`ObjID`- ja wrapper-luokan perusteella, ja parsata myös ravinteet, myrkyt, happi, CO2 ja
detritus oikein.

---

## Tehtävä 1 — `state.py`: Lisää puuttuvat aliluokat

Lisää seuraavat luokat olemassaolevien rinnalle:

```python
@dataclass
class Oxygen(Nutrient):
    """Dissolved oxygen, form='O2'"""
    threshold: float = 3.0  # mg/L, anoxia threshold

@dataclass
class CarbonDioxide(Nutrient):
    """CO2, form='CO2'"""
    import_equilibrium: bool = False

@dataclass
class Nitrate(Nutrient):
    """NO3 as N, form='NO3'"""
    pass

@dataclass
class Phosphorus(Nutrient):
    """Total soluble P, form='PO4'"""
    frac_avail: float = 1.0   # bioavailable fraction
    use_total_p: bool = False  # input as Total P flag

@dataclass
class Toxicant(StateVariable):
    """Organic toxicant (TToxics), e.g. PCBs"""
    ppb: float = 0.0
    carrier_nstate: int = -1  # linked carrier state index
```

---

## Tehtävä 2 — `io_utils.py`: ObjID-pohjainen tunnistus

Korvaa `_classify_state_variable()`-metodi (tai `_looks_like_plant/animal`) uudella logiikalla.

Lisää moduulitason kartta:

```python
# ObjID → Python-luokka -kartta
OBJID_MAP = {
    1001: "Animal",        # TAnimal
    1002: "Plant",         # TPlant / TAlgae
    1006: "Toxicant",      # TToxics — liuennut toksikantti (esim. PCBit, TCE)
    1013: "StateVariable", # Temperature (ympäristömuuttuja, ohitetaan)
    1021: "Nitrate",       # TNO3Obj
    1022: "Nutrient",      # TNH4Obj (ammonia)
    1025: "Phosphorus",    # TPhosphorus
    1026: "CarbonDioxide", # TCO2Obj
    1027: "Oxygen",        # TO2Obj
    1028: "Detritus",      # sedimenttidetritus (ei toksikantti)
    1039: "Volume",        # TVolume (ohitetaan, käsitellään Environmentissa)
}
```

> **Huom. (2026-04-24):** Alkuperäisessä reseptissä oli virhe — `1028` oli merkitty `"Toxicant"` ja `1006` puuttui kokonaan.
> Tarkistus Lake Ontario PCBs.txt -tiedostosta osoitti: ObjID 1006 = `"Dissolved org. tox"` (TToxics),
> ObjID 1028 = `"Refrac. sed. detritus"` / `"Labile sed. detritus"` (Detritus). Kartta korjattu.

Muuta `_parse_state_records()` niin että se:

1. Lukee `"ObjID":` ennen jokaista `TStateVariable`-blokkia
2. Käyttää `OBJID_MAP`-karttaa luokan valintaan nimen arvailun sijaan
3. Parsii `Phosphorus`-tapauksessa lisäksi `"FracAvail"` ja `"TP_IC"`-flagit
4. Parsii `Toxicant`-tapauksessa `"ppb"` ja `"Carrier"`-kentät
5. Parsii `Oxygen`-tapauksessa `"Threshhold"`-kentän

---

## Tehtävä 3 — `io_utils.py`: LoadingsRecord täydennys

Nykyinen parseri lukee vain `UseConstant`/`ConstLoad`. Lisää tuki NonPoint Source- ja
Point Source -latauksille, koska ravinteet (erityisesti Pyhäjärvi-fosfori) käyttävät niitä.

```python
# Parsittavat kentät LoadingsRecordista:
# "UseConstant" + "ConstLoad"          → jo toteutettu
# "Alt_UseConstant" + "Alt_ConstLoad"  → NonPoint/Point source constant
# Time Series Loadings: n=X; ...       → jo toteutettu
# Alt. Time Series Loadings: n=X; ...  → lisättävä
```

Luo `LoadingRecord`-dataclass joka sisältää kaikki kolme lähdettä (inflow, point source,
nonpoint source) ja palauta se tilamuuttujalle attribuuttina.

---

## Tehtävä 4 — `test_stage1.py`: Uudet testit

Lisää seuraavat testit:

```python
def test_pyhajarvi_nutrients_parsed():
    """Pyhäjärvi: fosfori ja happi löytyvät tilamuuttujista"""

def test_ontario_toxicants_parsed():
    """Lake Ontario: TToxics-objektit parsitaan Toxicant-luokiksi"""

def test_objid_classification():
    """ObjID 1027 → Oxygen, 1025 → Phosphorus, jne."""
```

---

## Prioriteettijärjestys

1. **Tehtävä 1** (`state.py` uudet luokat) — tarvitaan ennen tehtävää 2
2. **Tehtävä 2** (ObjID-kartta) — eniten vaikutusta, pienin riski
3. **Tehtävä 4** (testit) — aja jokaisen tehtävän jälkeen
4. **Tehtävä 3** (LoadingsRecord) — voi tehdä viimeisenä

---

## Tärkeä ohje

Älä muuta `Environment`-luokan rakennetta eikä olemassaolevia `Simulation.run()`- tai
`ODESolver`-metodeita. Muutokset rajoittuvat `state.py` ja `io_utils.py` tiedostoihin.
