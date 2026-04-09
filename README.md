#  German Energy Dashboard

A full-stack data science application for real-time monitoring, analysis, and forecasting of German electricity consumption. Built with a FastAPI backend, PostgreSQL database, and a multi-page Streamlit frontend.

> **Data sources:** [SMARD](https://www.smard.de/) (Bundesnetzagentur) for energy data · [Open-Meteo](https://open-meteo.com/) for weather data

---

## Screenshots

| Live Monitoring | Energy Mix |
|---|---|
| ![Live Monitoring](screenshots/live_monitoring.png) | ![Energy Mix](screenshots/energy_mix.png) |

| Compare Periods | Load Forecast |
|---|---|
| ![Compare Periods](screenshots/compare_periods.png) | ![Forecast](screenshots/forecast.png) |

---

## Features

- **Live Monitoring** - real-time electricity load tracking with alert threshold controls and drill-down focus window
- **Energy Mix** - stacked view of renewables (wind + solar) vs conventional generation with renewable share over time
- **Compare Periods** - normalized shape comparison of two custom time windows on a relative time axis
- **Load Forecast** - up to 72-hour ahead electricity demand forecast using a Random Forest model with recursive prediction
- **Automatic Data Ingestion** - background scheduler keeps the database updated without manual intervention

---

## System Architecture

```
SMARD API  ──┐
              ├──▶  ingest.py  ──▶  PostgreSQL  ──▶  FastAPI  ──▶  Streamlit
Open-Meteo ──┘       (ETL)            (DB)          (backend)     (frontend)
```

| Layer | Technology | Role |
|---|---|---|
| Data sources | SMARD API, Open-Meteo API | Energy + weather data |
| Ingestion | `ingest.py` | Fetch, clean, deduplicate, store |
| Database | PostgreSQL + SQLAlchemy ORM | Persistent time-series storage |
| Backend | FastAPI | REST API with scheduled ingestion |
| ML | scikit-learn RandomForest | Recursive load forecasting |
| Frontend | Streamlit (multi-page) | Interactive dashboard |

---

## Project Structure

```
├── main.py                  # FastAPI app + background scheduler
├── ingest.py                # ETL pipeline (fetch → clean → store)
├── forecast.py              # Feature engineering + RandomForest model
├── models.py                # SQLAlchemy ORM table definitions
├── schemas.py               # Pydantic response schemas
├── db.py                    # Database connection + session management
├── smard_client.py          # SMARD API client
├── weather_client.py        # Open-Meteo API client
├── pages/
│   ├── app.py               # Landing page
│   ├── live_monitoring.py   # Real-time load monitoring
│   ├── energy_mix.py        # Renewables vs conventional
│   ├── compare_periods.py   # Period-to-period comparison
│   └── forecast.py          # Load forecast viewer
├── screenshots/
└── requirements.txt
```

---

## How to Run

### 1. Clone the repository
```bash
git clone https://github.com/Pavithra-vgl/Energy_Dashboard-
cd Energy_Dashboard-
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up PostgreSQL
Create a database and set your connection string as an environment variable:
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/energy_db"
```

### 4. Start the FastAPI backend
```bash
uvicorn main:app --reload
```
The background scheduler will begin ingesting data automatically.

### 5. Launch the Streamlit dashboard
```bash
streamlit run pages/app.py
```

---

## ML Forecasting

The load forecast uses a **Random Forest Regressor** trained on time-series features:

- Hour of day, day of week
- Lag values (previous hours)
- Rolling mean
- Weather variables (temperature, wind speed)

Predictions use **recursive forecasting** - each predicted value is fed back as input for the next step, supporting forecast horizons of 6 to 72 hours.

---

## Data Pipeline

Raw API data goes through the following cleaning steps in `ingest.py`:

- Timestamp parsing (`pd.to_datetime`) and timezone normalization
- Numeric coercion and `NaN → None` conversion for database compatibility
- Duplicate prevention via overlapping window deletion before bulk insert
- `merge_asof` for aligning energy and weather timestamps that don't perfectly match
- Lag feature creation requires chronological sorting

---

## Tech Stack

`Python` · `FastAPI` · `PostgreSQL` · `SQLAlchemy` · `Streamlit` · `scikit-learn` · `pandas` · `Plotly` · `APScheduler` · `Open-Meteo API` · `SMARD API`

---

## Academic Context

Developed as part of the course **"Frameworks and Applications of Data Science"**
M.Sc. Data Science · Hochschule Fulda

---

## Author

**Pavithra Lakshmi Venugopal**
M.Sc. Data Science Student · Hochschule Fulda
