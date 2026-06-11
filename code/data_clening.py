import pandas as pd 
import matplotlib.pyplot as plt

df=pd.read_csv("waeather_data.csv")
df["datetime"]=pd.to_datetime(df["datetime"])
df=df.set_index("datetime")

daytime=df[df["ghi_wm2"]>0]
peak=df[df["ghi_wm2"]>600]
rainy = df[df["precipitation_mm"] > 0]

daily=df.resample("D").mean

print(daily)

# Add a new column — simple efficiency estimate
# Real panels lose efficiency as temperature rises above 25°C
# Standard temp coefficient is about 0.4% per degree
df["temp_loss_factor"]=1-(0.004 * df["temperature_c"])

# Simulated panel output (very simplified — PVLib will do this properly in Stage 3)
# Assume 100kW plant, 15% panel efficiency, 10m² per kW = 1000m² total
df["estimated_output_kw"]=df["ghi_wm2"] *0.15*5000 / 1000*df["temp_loss_factor"]

# Clip negative values (night time)
df["estimated_output_kw"]=df["estimated_output_kw"].clip(lower=0)


daily_energy = df["estimated_output_kw"].resample("D").sum()
print("\nEstimated daily energy (kWh):")
print(daily_energy)


fig, (ax1,ax2) = plt.subplots(2, 1, figsize=(12,6))

ax1.plot(df.index, df["ghi_wm2"], color="orange", label="GHI (W/m²)")
ax1.set_ylabel("Irradiance W/m²")
ax1.legend()


ax2.plot(df.index, df["estimated_output_kw"], color="green", label="Estimated Output (kW)")
ax2.set_ylabel("Power (kW)")
ax2.legend()

plt.tight_layout()
plt.savefig("output_plot.png")
plt.show()

print("Plot saved as output_plot.png")