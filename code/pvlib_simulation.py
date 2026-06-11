import pvlib
import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('display.width', None)

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

# --- Correctly sized for 100kW per inverter ---
# 20 panels/string × 17 strings = 340 panels × 300W = 102kW DC per inverter
system = pvlib.pvsystem.PVSystem(
    surface_tilt=20,
    surface_azimuth=180,
    module_parameters=module,
    inverter_parameters=inverter,
    temperature_model_parameters=temperature_model,
    modules_per_string=20,
    strings_per_inverter=17        # corrected
)

mc = pvlib.modelchain.ModelChain(system, location)
mc.run_model(weather)

single_inverter_ac = mc.results.ac
plant_output = single_inverter_ac * 5      # 5 inverters = 500kW

print(f"Peak output (single inverter): {single_inverter_ac.max()/1000:.2f} kW")
print(f"Peak output (full 500kW plant): {plant_output.max()/1000:.2f} kW")
print(f"Total energy: {plant_output.sum()/1000:.2f} kWh")

# --- Clear sky comparison ---
clearsky = location.get_clearsky(df.index)
mc_clear = pvlib.modelchain.ModelChain(system, location)
mc_clear.run_model(clearsky)
clear_output = mc_clear.results.ac * 5

fig, ax = plt.subplots(figsize=(12, 5))
(clear_output / 1000).plot(ax=ax, color="orange", label="Clear Sky — Theoretical Max", alpha=0.7)
(plant_output / 1000).plot(ax=ax, color="green", label="Real Weather Output")
ax.set_ylabel("Power (kW)")
ax.set_title("500kW Solar Plant — Clear Sky vs Real Weather")
ax.legend()
plt.tight_layout()
plt.savefig("pvlib_500kw_comparison.png")
plt.show()