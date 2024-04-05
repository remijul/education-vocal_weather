import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from sys import argv


def weather_forecast_from_coord(lat, lon, horizon=1):

    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # Make sure all required weather variables are listed here
    # The order of variables in hourly or daily is important to assign them correctly below
    url = "https://api.open-meteo.com/v1/meteofrance"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["temperature_2m", "relative_humidity_2m", "precipitation", "cloud_cover", "wind_speed_10m"],
        "timezone": "GMT",
        "past_days": 2,
        "forecast_days": horizon
    }
    responses = openmeteo.weather_api(url, params=params)
    
    if responses is None:
        weather_info = "Failed"
        weather_data = None
        weather_df = None
        
    else:
        weather_info = "Successed"

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]
        #print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
        #print(f"Elevation {response.Elevation()} m asl")
        #print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
        #print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

        # Process hourly data. The order of variables needs to be the same as requested.
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
        hourly_precipitation = hourly.Variables(2).ValuesAsNumpy()
        hourly_cloud_cover = hourly.Variables(3).ValuesAsNumpy()
        hourly_wind_speed_10m = hourly.Variables(4).ValuesAsNumpy()

        hourly_data = {"date": pd.date_range(
            start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
            end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
            freq = pd.Timedelta(seconds = hourly.Interval()),
            inclusive = "left"
        )}
        hourly_data["temperature_2m"] = hourly_temperature_2m
        hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
        hourly_data["precipitation"] = hourly_precipitation
        hourly_data["cloud_cover"] = hourly_cloud_cover
        hourly_data["wind_speed_10m"] = hourly_wind_speed_10m

        weather_df = pd.DataFrame(data = hourly_data)
        if weather_df.shape[0] > 0:
            weather_data = "OK"
        #print(weather_df)
    
    return({'weather_info' : weather_info,
            'weather_data': weather_data,
            'forecast_horizon' : horizon,
            'weather_df': weather_df})

# Test:
# weather_forecast_from_coord(lat=47.3900474, lon=0.6889268)

# Execution du script seulement s'il est appelé directement dans le terminal, sinon chargement uniquement sans exécution
if __name__ == "__main__":

    weather_forecast_from_coord(argv[1], argv[2])