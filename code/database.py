import sqlite3
import pvlib
import pandas as pd
import numpy as np

pd.set_option('display.width', None)

# STAGE 1 — RUN PVLIB SIMULATION
location = pvlib.location.Location(
    latitude=17.70,
    longitude=74.16,
    tz="Asia/Kolkata",
    altitude=662,
    name="Koregaon"
)

df = pd.read_csv(r"C:\Users\MUKKU\OneDrive\Desktop\digital twin\code\waeather_data.csv")
df["datetime"] = pd.to_datetime(df["datetime"])
df = df.set_index("datetime")
df.index = df.index.tz_localize("Asia/Kolkata")

weather = pd.DataFrame({
    "ghi": df["ghi_wm2"],
    "dni": df["dni_wm2"],
    "dhi": (df["ghi_wm2"] - df["dni_wm2"]).clip(lower=0),
    "temp_air": df["temperature_c"],
    "wind_speed": 1.0
})

sandia_modules = pvlib.pvsystem.retrieve_sam("SandiaMod")
module = sandia_modules["Canadian_Solar_CS6X_300M__2013_"]

sapm_inverters = pvlib.pvsystem.retrieve_sam("cecinverter")
inverter = sapm_inverters["ABB__PVI_CENTRAL_100_US__480V_"]

temperature_model = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS["sapm"]["open_rack_glass_glass"]

system = pvlib.pvsystem.PVSystem(
    surface_tilt=20,
    surface_azimuth=180,
    module_parameters=module,
    inverter_parameters=inverter,
    temperature_model_parameters=temperature_model,
    modules_per_string=11,
    strings_per_inverter=30
)

mc = pvlib.modelchain.ModelChain(system, location)
mc.run_model(weather)

single_inverter_ac = mc.results.ac
plant_output = single_inverter_ac * 5  # 5 inverters

cell_temp = mc.results.cell_temperature
dc_power = mc.results.dc

result_df = pd.DataFrame({
    "datetime": plant_output.index.strftime("%Y-%m-%d %H:%M:%S"),
    "plant_ac_kw": (plant_output / 1000).round(3),
    "plant_dc_kw": (dc_power["p_mp"] * 5 / 1000).round(3),
    "cell_temp_c": cell_temp.round(2),
    "ghi_wm2": df["ghi_wm2"].values,
    "ambient_temp_c": df["temperature_c"].values,
    "precipitation_mm": df["precipitation_mm"].values
})

print(f"Total plant_performance rows to store: {len(result_df)}")
print(result_df.head())

# STAGE 2 — CREATE / POPULATE plant_performance TABLE
conn = sqlite3.connect(r"C:\Users\MUKKU\OneDrive\Desktop\digital twin\code\solar_plant.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS plant_performance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        datetime TEXT NOT NULL,
        plant_ac_kw REAL,
        plant_dc_kw REAL,
        cell_temp_c REAL,
        ghi_wm2 REAL,
        ambient_temp_c REAL,
        precipitation_mm REAL
    )
""")

cursor.execute("DELETE FROM plant_performance")
result_df.to_sql("plant_performance", conn, if_exists="replace", index=False)

print("plant_performance table populated.")

# STAGE 3 — STRING-LEVEL DATA (150 strings: 11 panels x 30/inverter x 5 inverters)

NUM_STRINGS = 150
STRING_RATED_KW = 3.3  # 11 panels x 300W = 3.3kW per string

def generate_string_data(plant_ac_kw, num_strings=NUM_STRINGS):
    """
    Distributes plant output across strings with realistic +-5% variation.
    ~2% chance per timestep that one string has a fault (drops to 20-40% output).
    """
    base_per_string = plant_ac_kw / num_strings
    noise = np.random.normal(1.0, 0.05, num_strings)
    string_outputs = base_per_string * noise

    is_fault = np.zeros(num_strings, dtype=int)
    if np.random.random() < 0.02:
        fault_string = np.random.randint(0, num_strings)
        string_outputs[fault_string] *= np.random.uniform(0.2, 0.4)
        is_fault[fault_string] = 1

    return string_outputs.clip(min=0), is_fault

cursor.execute("DROP TABLE IF EXISTS string_data")
cursor.execute("""
    CREATE TABLE string_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        datetime TEXT NOT NULL,
        string_id INTEGER,
        string_kw REAL,
        is_fault INTEGER DEFAULT 0
    )
""")

print("Generating string-level data for daytime hours... this may take a minute")

np.random.seed(42)  # reproducible results

string_rows = []
for _, row in result_df.iterrows():
    plant_kw = row["plant_ac_kw"]

    # Skip nighttime hours - no point simulating strings with zero output
    if plant_kw <= 0:
        continue

    dt_str = row["datetime"]
    string_outputs, is_fault = generate_string_data(plant_kw)

    for sid in range(NUM_STRINGS):
        string_rows.append((dt_str, sid, float(string_outputs[sid]), int(is_fault[sid])))

cursor.executemany("""
    INSERT INTO string_data (datetime, string_id, string_kw, is_fault)
    VALUES (?, ?, ?, ?)
""", string_rows)

# Helpful index for fast lookups by datetime
cursor.execute("CREATE INDEX IF NOT EXISTS idx_string_datetime ON string_data(datetime)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_plant_datetime ON plant_performance(datetime)")

conn.commit()
conn.close()

print("=" * 50)
print("Database created: solar_plant.db")
print(f"Stored {len(result_df)} plant_performance rows")
print(f"Stored {len(string_rows)} string_data rows ({NUM_STRINGS} strings x daytime hours)")
print("=" * 50)