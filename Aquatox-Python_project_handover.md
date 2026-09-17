# Aquatox – Python: projektin siirto- ja jatkoyhteenveto (korjattu versio)

> **Tarkoitus:** Itsenäinen projektikonteksti tälle Aquatox-Python-projektille. Tarkoitettu annettavaksi seuraavalle kielimallille tai kehittäjälle.
>
> **Koostettu:** 18.8.2026
> **Projektin nimi:** Aquatox – Python (Akseli Savolaisen diplomityö, Tampereen yliopisto)
>
> **⚠️ Huomio edelliseen versioon:** Projektin dokumenttikansiossa oli tätä ennen tiedosto samalla nimellä, joka kuvasi **täysin väärää projektia** (OpenABM-Covid19-pohjainen epidemiasimulaattori, interventiot, kontaktiverkot jne.). Tämä ei liity mitenkään AQUATOX-projektiin, eikä sille löydy tukea mistään projektin oikeasta materiaalista (koodi, ChatGPT-keskustelu, diplomityö). Se on todennäköisesti syntynyt aiemmassa istunnossa väärän kontekstin sekoittumisesta. Tämä tiedosto korvaa sen kokonaan oikealla, lähteisiin perustuvalla sisällöllä.

---

## 1. Projektin ydin yhdellä kappaleella

Projektissa toteutetaan **Python-versiota EPA:n AQUATOX-vesistömallista** (Pascal/Delphi-pohjainen akvaattisten ekosysteemien differentiaaliyhtälömalli) osana **Akseli Savolaisen diplomityötä** "AI based software re-engineering – case AQUATOX" (Tampereen yliopisto, Automaatiotekniikan DI-ohjelma, tarkastajat Helena Leppäkoski ja Yrjö Majanne, valmistunut toukokuussa 2026). Työn aiheen antoi ja tekoälytyökalujen käytön mahdollisti **professori Mikko Kolehmainen (UEF)**. Työ on tapaustutkimus siitä, missä määrin tekoälyavusteinen ohjelmointi (ChatGPT + OpenAI Codex VS Codessa) soveltuu monimutkaisen legacy-järjestelmän uudelleenrakentamiseen, ja miten tarkasti tuloksena syntyvä Python-versio vastaa alkuperäisen AQUATOXin toimintaa.

---

## 2. Alkuperä: ChatGPT-keskustelu maaliskuu–elokuu 2025

Projektin ensimmäinen dokumentoitu vaihe löytyy Mikko Kolehmaisen ChatGPT-keskustelusta **"Python-mallinnus ekosysteemille"** (luotu 20.3.2025, päivitetty viimeksi 12.8.2025; URL: chatgpt.com/c/67dc16b2-...).

Keskustelun kulku:

1. Käyttäjä latasi kaksi tiedostoa: `aquatox_tech_doc_3.2.pdf` (EPA:n AQUATOX Release 3.2 -tekninen dokumentaatio) ja `LakePyhajarviFinland.txt` (AQUATOXilla tuotettu konkreettinen realisaatio Pyhäjärvestä), ja kysyi, voisiko tämän mallin tuottaa Pythonilla modulaarisesti.
2. ChatGPT arvioi tehtävän toteuttamiskelpoiseksi ja hahmotteli esimerkinomaisen luokkarakenteen (`Nutrient`, `Phytoplankton` -tyyppiset luokat + `scipy.integrate.solve_ivp`).
3. Käyttäjä täsmensi, ettei toteutusta tehdä vielä itse ("sen tekee toinen henkilö myöhemmin") ja pyysi ensimmäistä konkreettista esimerkkimoduulia: **virtausmoduuli (inflow/outflow/precipitation/evaporation)**. Tämä tuotettiin ChatGPTin Canvas-työkalulla nimellä "Flow Module" – tämä on sama vesitase-esimerkki (dV/dt = I − O − E), joka päätyi myöhemmin diplomityön lukuun 3.5–3.6 "Proof of Concept" -esimerkkinä ja joka vastaa projektin dokumenttikansion tiedostoa `simWaterflow.py`.
4. Loppuosa keskustelusta on käytännön työkaluohjausta: VS Coden asennus, Git for Windows, GitHub-tilin yhdistäminen, `git config` (nimi/sähköposti), PATH-ongelman ratkaisu, ensimmäinen commit/push. Tarkoitus oli valmistella ympäristö sille henkilölle (Akseli Savolainen), joka jatkoi varsinaista toteutusta.
5. Keskustelu päättyy toteamukseen, että koodi saatiin ajettua VS Codessa ja työtä jatketaan myöhemmin muualla.

Muuta ChatGPT-historiaa käytiin läpi laajemmin (n. 300 keskustelua koko tililtä), eikä muita tähän projektiin liittyviä keskusteluja löytynyt. Kaksi löydöstä ovat vain löyhästi sivuavia eivätkä liity itse Python-toteutukseen:
- **"Kallavesi site kuvaus"** (huhtikuu 2026): EU Horizon -hakemuksen (HORIZON-CL6-2026-01-BIODIV-01, "Living labs...") site-kuvaus Kallavedelle – eri hanke, ei Aquatox-Pythonia.
- **"Mallintamisen kalvot ehdotus"** (syyskuu 2025): luentokalvoehdotus järvien ekologisesta mallintamisesta yleisellä tasolla – ei koske tätä koodiprojektia suoraan.

Varsinainen syväluotaava toteutustyö (Codex, VS Code, GitHub-repot) on tehty Akseli Savolaisen omilla tunnuksilla eikä näy tässä ChatGPT-tilissä.

---

## 3. Menetelmä: kolmivaiheinen re-engineering-prosessi

Diplomityö noudattaa kirjallisuudesta johdettua kolmivaiheista mallia:

1. **Reverse engineering** – AQUATOXin ydinlogiikan ja käsitteiden ymmärtäminen tekoälyavusteisesti (dokumentaation ja julkisen Pascal/Delphi-koodin pohjalta).
2. **Alteration** – kohdearkkitehtuurin suunnittelu (UML-luokka- ja aktiviteettikaaviot, tuotettu ChatGPTn UML-merkinnällä ja visualisoitu PlantUML:llä).
3. **Forward engineering** – osittainen toteutus Pythonilla, VS Code + OpenAI Codex -yhdistelmällä.

Tutkimuskysymys jaettiin kolmeen tasoon: **Taso 0** (haasteiden tunnistus/dokumentointi), **Taso 1** (moduulipohjainen toteutussuunnitelma), **Taso 2** (simulaatioajot uudella versiolla ja tulosten vertailu vanhaan – tämä saavutettiin osittain fysikaalisen kerroksen osalta).

---

## 4. Koodirepositoriot

Projektissa on kaksi GitHub-repositoriota (Akseli Savolaisen tilillä `savolaks`):

| Repo | Sisältö |
|---|---|
| `Aquatox-work` | Uusi Python-toteutus. Aktiivinen branch: **`savolainen2026`** (tila diplomityössä kuvattu 28.2.2026 asti). |
| `AQUATOX-master` | Peilattu legacy-koodi (alkuperäinen Pascal/Delphi AQUATOX, julkinen EPA-lähde). |

Kehitysympäristö: **VS Code + GitHub + OpenAI Codex -laajennus**. Testaus tehdään tällä hetkellä manuaalisesti Excelissä tulosten vertailuun; diplomityö suosittelee automatisoidun testipaketin rakentamista jatkoa varten, koska sitä ei vielä ole kattavasti.

**Huom:** Tämän Claude-projektin dokumenttikansiossa oleva koodi (`core.py`, `state.py`, `io_utils.py`, `typing_ext.py`, `io_utils.py`, `test_stage1.py`, `main.py`, `README.md`) on merkitty "Stage-1 skeleton" -tasoiseksi ja luotu 23.4.2026 – se on selvästi **yksinkertaisempi/aikaisempi tilannekuva** kuin diplomityössä (helmikuu–toukokuu 2026) kuvattu `savolainen2026`-branch, jossa on jo mm. CLI-parametrit, Foodweb-luokka, lämpötila/tuuli/valo/pH/TSS-ajurit ja "wrap around annual cycle" -algoritmi. Todellinen ajantasainen tila on GitHubissa, ei näissä paikallisissa tiedostoissa – tarkista aina repo ennen jatkokehitystä.

---

## 5. Arkkitehtuuri (per diplomityön luvut 4–5, sellaisena kuin se on toteutunut)

```text
Simulation  (orkestroi: env, solver, state_vars; load_scenario(), run(), output_results())
 ├── Environment  (tilavuus, pinta-ala, syvyydet, inflow/outflow/lämpötila/tuuli/valo/pH/TSS-sarjat)
 ├── ODESolver    (Euler toteutettu; UML:ssä varaus muille menetelmille)
 └── StateVariable (abstrakti kanta)
      ├── Nutrient   (NH4/NO3/PO4/O2/CO2 – muodot)
      ├── Detritus   (labile/refractory; water/sediment)
      └── Biota
           ├── Plant
           └── Animal

ScenarioIO / Utils   – erillinen kerros: JSON-skenaarion parsinta, tilamuuttujien tunnistus
                        nimen perusteella, tulosten CSV/Excel-vienti
Foodweb               – erotettiin StateVariable-luokista omaksi luokakseen toteutuksen aikana
                        (Codexin ehdottama, kirjoittajan hyväksymä arkkitehtuurimuutos)
```

Keskeinen ero alkuperäiseen suunnitelmaan: `Environment` ja `ScenarioIO` kasvoivat merkittävästi suunniteltua laajemmiksi (ympäristöajureiden lisääntyessä), ja predaatiologiikka siirrettiin omaksi `Foodweb`-luokakseen pois `StateVariable`-attribuuteista.

### Rajaukset (tietoisesti tehdyt, UEF-tutkimusryhmän vaatimuksesta)
- **Vain komentorivikäyttöliittymä (CLI)** – ei GUI:ta.
- **Alustus vain legacy-AQUATOXin tuottamasta JSON-tiedostosta** – uutta ja vanhaa versiota ajetaan rinnakkain, kunnes/jos uusi versio joskus korvaa vanhan kokonaan.
- **Toteutus rajattu fysikaaliseen kerrokseen** (vesitase, lämpötilakerrostuminen, tuuli, valo, pH, TSS/epäorgaaninen sedimentti). **Kemialliset ja biologiset prosessit (`rate()`-funktiot) ovat vielä placeholder-tasolla** – luokkarakenne on valmis, mutta todelliset prosessiyhtälöt (kasvu, hajotus, ravinnekierto, toksikologia) puuttuvat.

---

## 6. Regressiotestaus ja tulokset (diplomityön luku 6, toukokuu 2026 tilanne)

Menetelmä: aja skenaario legacy-AQUATOX R3.2:lla → vie JSON-tulostiedosto → tuo Python-versioon alustukseksi → aja Python-versiolla → vertaa tuloksia.

**Testatut sivustot:**
- **Lake Pyhäjärvi (Suomi)** – päätestitapaus: alkuarvot, vesitilavuus, lämpötila, tuuli, valo, pH, ravintoverkko.
- **Zollner Creek (OR, USA)** – käytetty TSS-testaukseen, koska Pyhäjärvi-aineistossa ei ollut TSS-aikasarjaa (huom: puro, ei järvi – eri sivustotyyppi).

**Havainnot:**
- **Vesitilavuus:** Python-versio täsmää AQUATOXiin hyvin. Lisäksi havaittiin, että alkuperäinen AQUATOX itse asiassa epäonnistuu omassa "wrap around annual cycle" -algoritmissaan (satunnaisia tilavuuspudotuksia) – Python-versio käsittelee tämän intuitiivisemmin oikein.
- **Ravintoverkko (foodweb):** predaatiopreferenssit ja egestiokertoimet täsmäävät AQUATOXiin – alustus onnistuu luotettavasti.
- **Epilimnion-lämpötila:** täsmää hyvin.
- **Hypolimnion-lämpötila:** eroja havaittu, osin selittyvissä eri syöttösarjojen käsittelyllä; myös alkuperäisessä AQUATOXissa havaittiin kyseenalaisia arvoja (esim. perusteeton 0.3 °C -piikki).
- **Tuuli:** oletusarvoinen Fourier-sarja -algoritmi onnistuttiin toteuttamaan löytämällä harmoniset kertoimet vanhasta Pascal-lähdekoodista tekoälyn avulla ("one-shot" -toteutus). Myös tässä Python-versio tuotti intuitiivisemman/vakaamman tuloksen kuin legacy-AQUATOXin oma virheellinen toteutus.
- **Valo:** rakenteellinen ero – Python käyttää lineaarista interpolointia kuukausittaisten ankkuripisteiden välillä, jolloin kevään valoisuuden nousu alkaa aikaisemmin kuin legacy-AQUATOXissa. Erillistä photoperiod-alimallia (CalculatePhotoperiod) ei ole vielä toteutettu.
- **pH:** käsitellään puhtaasti ulkoisena ajurina (ei kemiaa vielä) – toimii molemmissa versioissa samalla logiikalla.
- **TSS:** ajurina ilman fysikaalis-kemiallis-biologista dynamiikkaa; vertailu vaikeaa, koska Zollner Creek -referenssiajo AQUATOXissa sisälsi täyden mallin interaktioita, joita Python-versiossa ei vielä ole.

**Puuttuvat/avoimet:** seitsemän tilamuuttujaa jää alustuksessa yleiselle ("undisplayed") tasolle – syy liittyy oletettavasti JSON-syötteen metadataan, ei vielä ratkaistu.

---

## 7. Diplomityön johtopäätökset ja suositukset

- Tekoälyavusteinen re-engineering osoittautui **erittäin tehokkaaksi**: uusi versio toisti legacy-toiminnallisuuden fysikaalisella kerroksella ja jopa korjasi legacy-AQUATOXin omia bugeja (tuuli, vesitase-poikkeamat).
- Onnistumisen edellytykset: (1) selkeä arkkitehtuurivisio ja jatkuva sen vahtiminen ("tekoäly pitää silloin tällöin ohjata takaisin linjaan"), (2) pienet, testattavat inkrementit ennen commitointia, (3) automatisoitu testauskehikko olisi jatkossa tarpeen (ei vielä kattavasti käytössä).
- **Kirjoittajan esittämä vaihtoehtoinen strategia jatkoa varten** (ei vielä toteutettu/päätetty): koko järjestelmän täydellinen Python-muunnos saattaa olla vähemmän välttämätön kuin alun perin ajateltiin, koska tekoäly kykenee todennäköisesti muokkaamaan myös alkuperäistä Pascal/Delphi-koodia suoraan. Vaihtoehtona ehdotetaan legacy-koodin oman haarautuneen version ylläpitoa ja kalibrointiin tarvittavien osien kohdennettua muokkausta tekoälyn avulla sen sijaan, että koko järjestelmä käännetään Pythonille. Tätä ei ole tutkittu/varmistettu tässä työssä – se on avoin jatkopäätös UEF-tutkimusryhmälle.
- Seuraava luonnollinen vaihe (ei vielä tehty): kemiallisten ja biologisten prosessiyhtälöiden toteutus (`rate()`-funktiot), sekä automaattisen testipatterin rakentaminen.

---

## 8. Projektin dokumenttikansion sisältö (tämä Claude-projekti)

| Tiedosto | Rooli |
|---|---|
| `aquatox_tech_doc_3.2.pdf` | EPA:n AQUATOX 3.2 -tekninen dokumentaatio (alkuperäinen lähde, sama joka ladattiin ChatGPT-keskusteluun). |
| `AI based software reengineering case AQUATOX Savolainen 2026.pdf` | **Akseli Savolaisen valmis diplomityö** – tärkein ja luotettavin lähde projektin tilasta, arkkitehtuurista ja tuloksista. |
| `LakePyhajarviFinland.txt` | AQUATOXin tuottama realisaatio Pyhäjärvestä – päätestiaineisto. |
| `Lake Ontario PCBs.txt`, `Lake Jesup FL.txt`, `Skensved Denmark TCE.txt` | Muita AQUATOXin esimerkkiaineistoja (mahdollisesti tulevaa laajempaa regressiotestausta varten – ei mainittu käytetyksi diplomityön testeissä). |
| `pyhajarvi_state_variables.json` / `.csv` | `ScenarioIO.export_state_variables()`-funktion tuottama tilamuuttujien kartoitus Pyhäjärvi-aineistosta. |
| `core.py`, `state.py`, `io_utils.py`, `typing_ext.py`, `main.py`, `test_stage1.py`, `README.md`, `requirements.txt`, `__init__.py` | **"Stage-1 skeleton"** -tasoinen koodinäyte (23.4.2026) – yksinkertaisempi kuin diplomityössä kuvattu ajantasainen `savolainen2026`-branch. Käytettävissä rakenteen ymmärtämiseen, mutta ei korvaa GitHub-repon tarkistamista. |
| `simWaterflow.py` | Alkuperäinen vesitase-esimerkki (PyCharm-tyylinen skripti) – vastaa ChatGPT-keskustelun "Flow Module" -esimerkkiä / diplomityön luvun 3.6 "Proof of Concept" -koodia. |
| `Uusi Tekstitiedosto.txt` | Tyhjä/nimeämätön tiedosto, sisältöä ei tarkistettu tämän yhteenvedon yhteydessä. |

---

## 9. Seuraavan kielimallin/kehittäjän toimintaohje

1. **Älä käytä vanhaa (korvattua) handover-tiedostoa** – se kuvasi väärää projektia.
2. Lue tarvittaessa `AI based software reengineering case AQUATOX Savolainen 2026.pdf` kokonaan – se on kattavin ja luotettavin kuvaus arkkitehtuurista, rajauksista ja testituloksista.
3. Tarkista GitHubista `Aquatox-work`-repon `savolainen2026`-branch nykytila ennen muutoksia – paikallinen `core.py` ym. on vanhentunut tilannekuva (huhtikuu 2026).
4. Muista rajaukset: CLI-only, alustus legacy-AQUATOXin JSON-viennistä, fysikaalinen kerros toteutettu, kemia/biologia vielä placeholder.
5. Ennen laajaa jatkokehitystä kannattaa harkita diplomityön luvun 7 vaihtoehtoista strategiaa (legacy-koodin kohdennettu muokkaus vs. täysi Python-muunnos) yhdessä käyttäjän kanssa – tätä ei ole vielä päätetty.

---

## 10. Provenienssi

Tämä yhteenveto perustuu kolmeen lähteeseen, jotka kaikki löytyivät ja tarkistettiin 18.8.2026: (1) käyttäjän ChatGPT-tililtä viety keskustelu "Python-mallinnus ekosysteemille" (67dc16b2, 20.3.–12.8.2025), (2) Akseli Savolaisen diplomityö (projektin tiedostoissa), ja (3) projektin dokumenttikansion koodinäytteet. Ristiriitatilanteessa diplomityö ja GitHub-repo ovat luotettavampia kuin tämän kansion koodinäytteet, koska ne ovat myöhäisempiä ja kattavampia.
