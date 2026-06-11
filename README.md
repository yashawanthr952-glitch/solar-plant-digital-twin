# 🌞 Solar Power Plant Digital Twin

A full-stack Digital Twin of a 400kW solar power plant — integrating real weather data, physics-based PV simulation, a REST API backend, and live 3D visualization in Unity 6.

> Final year project by an Electrical Engineering student at VJTI Mumbai, targeting ER&D roles in Industrial IoT, Digital Twin, and Energy Systems.

---

## 🎥 Demo Video

[![Watch Demo](https://img.shields.io/badge/▶%20Watch%20Demo-YouTube-red?style=for-the-badge&logo=youtube)](https://youtu.be/bZ3elp4rmAc)

---

## 🖼️ Screenshots

### Normal Operation — GREEN
![Green State](assets/green_state.png)

### Fault / Low Output — RED
![Red State](assets/red_state.png)

---

## 🏗️ System Architecture

```
┌──────────────────┐     ┌───────────────────┐     ┌──────────────────┐
│  Open-Meteo API  │────▶│  Python Pipeline  │────▶│ SQLite Database  │
│  Weather Data    │     │  PVLib Simulation │     │  4258 Records    │
│  Full Year 2025  │     │  Pandas Processing│     │  Full Year Data  │
└──────────────────┘     └───────────────────┘     └────────┬─────────┘
                                                            │
                                                            ▼
┌──────────────────┐     ┌───────────────────┐     ┌──────────────────┐
│  Unity 6         │◀────│  FastAPI          │◀────│  6 REST          │
│  3D Visualization│     │  REST API Server  │     │  Endpoints       │
│  Live Color Maps │     │  localhost:8000   │     │  JSON Responses  │
└──────────────────┘     └───────────────────┘     └──────────────────┘
```

---

## ⚡ Tech Stack

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![PVLib](https://img.shields.io/badge/PVLib-Physics%20Simulation-orange?style=flat-square)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Processing-purple?style=flat-square&logo=pandas)
![FastAPI](https://img.shields.io/badge/FastAPI-REST%20API-green?style=flat-square&logo=fastapi)
![SQLite](https://img.shields.io/badge/SQLite-Database-lightblue?style=flat-square&logo=sqlite)
![Blender](https://img.shields.io/badge/Blender-3D%20Modeling-orange?style=flat-square&logo=blender)
![Unity](https://img.shields.io/badge/Unity-6-black?style=flat-square&logo=unity)

---

## 🌱 Plant Specifications

| Parameter | Value |
|---|---|
| Plant Capacity | 400 kW |
| Location | Koregaon, Maharashtra (17.7°N, 74.16°E) |
| Panel Model | Canadian Solar CS6X 300W |
| Inverter | ABB PVI Central 100kW × 5 |
| Panel Tilt | 20° South-facing |
| String Config | 11 panels/string × 30 strings/inverter |
| Simulation Period | Full Year 2025 (8760 hours) |
| Annual Yield | ~660 MWh/year |

---

## 🗂️ Project Structure

```
solar-plant-digital-twin/
│
├── data_fetching.py        # Stage 1: Open-Meteo API — fetch full year weather data
├── data_cleaning.py        # Stage 2: Pandas — process, filter, visualize
├── pvlib_simulation.py     # Stage 3: PVLib — physics-based plant simulation
├── database.py             # Stage 4: SQLite — store 4258 daytime records
├── query_test.py           # Stage 4: SQL queries — monthly analysis
├── api.py                  # Stage 5: FastAPI — 6 REST endpoints
│
├── waeather_data.csv       # Raw weather data — Open-Meteo historical archive
├── solar_plant.db          # SQLite database — simulation output
│
├── assets/
│   ├── green_state.png     # Unity screenshot — normal operation
│   ├── red_state.png       # Unity screenshot — fault condition
│   └── yearly_plot.png     # PVLib yearly performance chart
│
└── SolarPlant_DigitalTwin/ # Unity 6 project
    └── Assets/
        ├── Scripts/
        │   ├── APIManager.cs       # HTTP polling — UnityWebRequest coroutine
        │   └── PlantVisualizer.cs  # Real-time material color updates
        ├── Models/                 # 5 Blender-modeled FBX assets
        └── Materials/
```

---

## 🎨 3D Asset Modeling — Blender

All 5 plant assets were **modeled from scratch in Blender** — no pre-made or downloaded assets used.

| Asset | Details |
|---|---|
| ☀️ Solar Panel | Monocrystalline panel with frame, glass layer, and cell grid detail |
| ⚡ Inverter Cabinet | ABB-style cabinet with ventilation grilles and control panel |
| 🔌 Power Transformer | Oil-cooled transformer with cooling fins and HV/LV bushings |
| 🏭 HT Switchgear Bay | High tension bay with insulators and bus bars |
| 🏠 Substation Building | Control room with doors, windows, and cable routing |

Exported as FBX with applied transforms and imported into Unity 6.

---

## 📊 Simulation Results

### Monthly Energy Yield

| Month | Avg Output (kW) | Total Energy (kWh) | Notes |
|---|---|---|---|
| January | 164.66 | 56,149 | Clear winter sky |
| February | 182.53 | 56,951 | Peak clear sky |
| March | 177.96 | 66,201 | Equinox — sun overhead |
| April | 174.01 | 62,644 | High irradiance |
| May | 142.39 | 52,685 | Pre-monsoon haze |
| June | 139.04 | 51,028 | Monsoon begins |
| July | 115.66 | 44,530 | Peak monsoon — lowest |
| August | 136.78 | 51,157 | Monsoon continues |
| September | 144.48 | 51,724 | Equinox — recovery |
| October | 155.58 | 56,321 | Post-monsoon clear |
| November | 168.13 | 55,482 | Clear sky returns |
| December | 167.73 | 54,847 | Clear winter sky |

**Peak output hour:** 349 kW on 2025-03-22 13:00 (GHI: 984 W/m²)
**Annual yield:** ~660 MWh/year (~1650 kWh/kWp — within real-world range)

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| GET | `/plant/status` | Latest plant reading |
| GET | `/plant/recent` | Last 24 hours of data |
| GET | `/plant/monthly` | Monthly energy summary |
| GET | `/plant/performance_ratio` | Monthly performance ratio vs theoretical |
| GET | `/plant/faults` | Fault detection — hours below 70% expected output |

Interactive docs available at: `http://127.0.0.1:8000/docs`

---

## 🎮 Unity Real-Time Visualization

Unity polls the FastAPI every **5 seconds** using `UnityWebRequest` coroutines. Equipment materials update instantly based on live data.

| Color | Plant Status | Condition |
|---|---|---|
| 🟢 Green | Normal Operation | AC Power > 200 kW |
| 🟡 Yellow | Low Output | AC Power 50–200 kW |
| 🔴 Red | Fault / Very Low | AC Power < 50 kW |
| 🔵 Blue | Night Mode | GHI = 0 W/m² |

---

## ⚙️ Setup & Run

### Prerequisites
```bash
py -m pip install requests pandas matplotlib pvlib fastapi uvicorn
```

### 1 — Fetch Weather Data
```bash
py data_fetching.py
```

### 2 — Run PVLib Simulation
```bash
py pvlib_simulation.py
```

### 3 — Build Database
```bash
py database.py
```

### 4 — Start API Server
```bash
py -m uvicorn api:app --reload
```
API live at: `http://127.0.0.1:8000`
Docs at: `http://127.0.0.1:8000/docs`

### 5 — Open Unity
Open `SolarPlant_DigitalTwin` in Unity 6. Press Play. Ensure API server is running.

---

## 🧠 What I Learned

- Calling REST APIs and parsing JSON in Python
- Time-series data processing and resampling with Pandas
- Solar physics — GHI, DNI, DHI, cell temperature modeling, performance ratio
- PVLib ModelChain for full plant simulation with real panel/inverter specs
- SQLite database design and SQL querying for time-series data
- Building REST APIs with FastAPI and serving JSON to external clients
- 3D modeling of industrial equipment from scratch in Blender
- FBX export pipeline from Blender to Unity
- Unity C# scripting — UnityWebRequest, coroutines, material color manipulation
- Connecting a Python backend to a Unity 3D frontend via HTTP

---

## 👤 Author

**Yashwanth Reddy**
Final Year Electrical Engineering — VJTI Mumbai (2026)

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Yashwanth%20Reddy-blue?style=flat-square&logo=linkedin)](https://linkedin.com/in/yashwanth-reddy-292998272)
[![GitHub](https://img.shields.io/badge/GitHub-yashawanthr952--glitch-black?style=flat-square&logo=github)](https://github.com/yashawanthr952-glitch)

---

## 📄 License

MIT License — free to use and modify with attribution.
