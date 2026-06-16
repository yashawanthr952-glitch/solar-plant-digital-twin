from fastapi import FastAPI, Query
import sqlite3
import pandas as pd
from datetime import datetime
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = r"C:\Users\MUKKU\OneDrive\Desktop\digital twin\code\solar_plant.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row      # returns dict-like rows
    return conn

# --- Endpoint 1: API health check ---
@app.get("/")
def root():
    return {"status": "Solar Plant Digital Twin API Running"}

# --- Endpoint 2: Current plant status ---
# Returns the most recent record in the database
@app.get("/plant/status")
def plant_status():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM plant_performance 
        ORDER BY plant_ac_kw DESC    
        LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    return dict(row)

# --- Endpoint 3: Last 24 hours of data ---
@app.get("/plant/recent")
def plant_recent():
    conn = get_db()
    df = pd.read_sql("""
        SELECT datetime, plant_ac_kw, ghi_wm2, ambient_temp_c
        FROM plant_performance
        ORDER BY datetime DESC
        LIMIT 24
    """, conn)
    conn.close()
    return df.to_dict(orient="records")

# --- Endpoint 4: Monthly summary ---
@app.get("/plant/monthly")
def plant_monthly():
    conn = get_db()
    df = pd.read_sql("""
        SELECT 
            substr(datetime, 1, 7) as month,
            ROUND(AVG(plant_ac_kw), 2) as avg_kw,
            ROUND(SUM(plant_ac_kw), 0) as total_kwh,
            ROUND(MAX(plant_ac_kw), 2) as peak_kw
        FROM plant_performance
        GROUP BY month
        ORDER BY month
    """, conn)
    conn.close()
    return df.to_dict(orient="records")

# --- Endpoint 5: Performance ratio ---
# Compares actual vs theoretical clear sky output
@app.get("/plant/performance_ratio")
def performance_ratio():
    conn = get_db()
    df = pd.read_sql("""
        SELECT 
            substr(datetime, 1, 7) as month,
            ROUND(AVG(plant_ac_kw), 2) as avg_actual_kw
        FROM plant_performance
        GROUP BY month
        ORDER BY month
    """, conn)
    conn.close()
    
    # Theoretical max for this plant is ~350kW at peak
    # PR = actual / theoretical
    df["performance_ratio"] = (df["avg_actual_kw"] / 350 * 100).round(1)
    return df.to_dict(orient="records")

# --- Endpoint 6: Fault detection ---
# Flags hours where output is significantly below expected for the irradiance
@app.get("/plant/faults")
def detect_faults():
    conn = get_db()
    df = pd.read_sql("""
        SELECT datetime, plant_ac_kw, ghi_wm2, cell_temp_c
        FROM plant_performance
        WHERE ghi_wm2 > 400
    """, conn)
    conn.close()
    
    # Expected output based on GHI ratio
    df["expected_kw"] = (df["ghi_wm2"] / 1000) * 350
    df["actual_vs_expected"] = (df["plant_ac_kw"] / df["expected_kw"] * 100).round(1)
    
    # Flag anything below 70% of expected as a fault
    faults = df[df["actual_vs_expected"] < 70]
    
    return {
        "total_fault_hours": len(faults),
        "faults": faults[["datetime", "plant_ac_kw", "expected_kw", "actual_vs_expected"]].to_dict(orient="records")
    }
# --- Endpoint 7:DATE SELECTION ---
@app.get("/plant/data")
def get_plant_data(datetime_str: str = Query(default=None)):
    conn = get_db()
    if datetime_str:
        df = pd.read_sql("""
            SELECT * FROM plant_performance
            WHERE datetime >= ?
            ORDER BY datetime ASC
            LIMIT 1
        """, conn, params=(datetime_str,))
    else:
        df = pd.read_sql("""
            SELECT * FROM plant_performance
            ORDER BY plant_ac_kw DESC
            LIMIT 1
        """, conn)
    conn.close()
    if df.empty:
        return {"error": "No data found"}
    return df.iloc[0].to_dict()

@app.post("/plant/set_datetime")
def set_datetime(datetime_str: str = Query(...)):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    cursor.execute("""
        INSERT OR REPLACE INTO settings (key, value)
        VALUES ('selected_datetime', ?)
    """, (datetime_str,))
    conn.commit()
    conn.close()
    return {"set": datetime_str}

@app.get("/plant/current")
def get_current():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    cursor.execute("SELECT value FROM settings WHERE key='selected_datetime'")
    row = cursor.fetchone()
    dt = row[0] if row else None
    conn.close()

    # Fix format — replace T with space to match database format
    if dt:
        dt = dt.replace("T", " ")

    conn2 = sqlite3.connect(DB_PATH)
    if dt:
        df = pd.read_sql("""
            SELECT * FROM plant_performance
            WHERE datetime >= ?
            ORDER BY datetime ASC
            LIMIT 1
        """, conn2, params=(dt,))
    else:
        df = pd.read_sql("""
            SELECT * FROM plant_performance
            ORDER BY plant_ac_kw DESC
            LIMIT 1
        """, conn2)
    conn2.close()

    if df.empty:
        return {"error": "No data"}
    return df.iloc[0].to_dict()