import sqlite3
import pvlib
import pandas as pd

pd.set_option('display.width', None)

# --- Run your simulation first (copy from pvlib_simulation.py) ---
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
plant_output = single_inverter_ac * 5

#Also get DC power and cell temperature
cell_temp = mc.results.cell_temperature
dc_power = mc.results.dc

#Build final DataFrame
result_df = pd.DataFrame({
    "datetime": plant_output.index.strftime("%Y-%m-%d %H:%M:%S"),
    "plant_ac_kw": (plant_output / 1000).round(3),
    "plant_dc_kw": (dc_power["p_mp"] * 5 / 1000).round(3),
    "cell_temp_c": cell_temp.round(2),
    "ghi_wm2": df["ghi_wm2"].values,
    "ambient_temp_c": df["temperature_c"].values,
    "precipitation_mm": df["precipitation_mm"].values
})

# Remove nighttime rows to save space
result_df = result_df[result_df["plant_ac_kw"] > 0]

print(f"Total rows to store: {len(result_df)}")
print(result_df.head())

#Create SQLite database 
conn = sqlite3.connect(r"C:\Users\MUKKU\OneDrive\Desktop\digital twin\code\solar_plant.db")
cursor = conn.cursor()

# Create table
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

# Clear old data if rerunning
cursor.execute("DELETE FROM plant_performance")

# Insert all rows
result_df.to_sql("plant_performance", conn, if_exists="replace", index=False)

conn.commit()
conn.close()

print("Database created: solar_plant.db")
print(f"Stored {len(result_df)} rows")