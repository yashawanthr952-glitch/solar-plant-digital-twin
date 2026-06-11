import requests
import csv

url=url = "https://archive-api.open-meteo.com/v1/archive"


params={
    "latitude":17.70,
    "longitude":74.16,
    "hourly": "temperature_2m,shortwave_radiation,direct_radiation,precipitation",
    "timezone" : "Asia/Kolkata",
    "start_date": "2025-01-01",      # replace forecast_days with this
    "end_date": "2025-12-31"         # full year 2025
}

response=requests.get(url,params=params)

print("Status code:",response.status_code)
data =response.json()

hourly=data["hourly"]
times=hourly["time"]

temperature=hourly["temperature_2m"]
ghi=hourly["shortwave_radiation"]               # Global Horizontal Irradiance in W/m²
dni=hourly["direct_radiation"]  
precipitation=hourly["precipitation"]                        # Direct Normal Irradiance

with open("waeather_data.csv","w",newline="") as file:
    writer=csv.writer(file)

    writer.writerow(["datetime", "temperature_c", "ghi_wm2", "dni_wm2","precipitation_mm"])


    for i in range(len(times)):
        writer.writerow([times[i], temperature[i], ghi[i], dni[i],precipitation[i]])


print("saved to weather_data.csv")