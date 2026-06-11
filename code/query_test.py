import sqlite3
import pandas as pd

conn = sqlite3.connect(r"C:\Users\MUKKU\OneDrive\Desktop\digital twin\code\solar_plant.db")

# Query 1 — Latest 5 records
print("=== Latest 5 records ===")
df = pd.read_sql("SELECT * FROM plant_performance ORDER BY datetime DESC LIMIT 5", conn)
print(df)

# Query 2 — Peak power day
print("\n=== Top 5 highest output hours ===")
df2 = pd.read_sql("SELECT datetime, plant_ac_kw, ghi_wm2 FROM plant_performance ORDER BY plant_ac_kw DESC LIMIT 5", conn)
print(df2)

# Query 3 — Monthly average output
print("\n=== Monthly average output ===")
df3 = pd.read_sql("""
    SELECT 
        substr(datetime, 1, 7) as month,
        ROUND(AVG(plant_ac_kw), 2) as avg_kw,
        ROUND(SUM(plant_ac_kw), 0) as total_kwh
    FROM plant_performance
    GROUP BY month
    ORDER BY month
""", conn)
print(df3)

conn.close()