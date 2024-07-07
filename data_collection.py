import Adafruit_DHT
import time
import requests
import json
import pandas as pd
import gspread

sa = gspread.service_account(
    filename='sensing-and-iot-project-697ae27b6369.json')

sh = sa.open("Sensing IoT Data")

wks = sh.worksheet("Data2")

# Sensor setup
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

# Initialize dataframe
df = pd.DataFrame(columns=['Time', 'Sensor Temp (°C)',
                  'Sensor Humidity (%)', 'API Temp (°C)', 'API Humidity (%)'])

while True:
    # Keep trying to read from sensor until successful
    while True:
        sensor_humidity, sensor_temperature = Adafruit_DHT.read(
            DHT_SENSOR, DHT_PIN)
        if sensor_humidity is not None and sensor_temperature is not None:
            break
        else:
            print('Sensor failure. Retrying...')
            time.sleep(1)  # Wait a bit before retrying

    # Get data from API
    response = requests.get(
        "http://api.weatherapi.com/v1/forecast.json?key=7decb912832e434da84124827231411&q=hounslow&days=1&aqi=no&alerts=no")
    data = response.json()
    api_time = data['current']['last_updated']
    api_temp = data['current']['temp_c']
    api_humidity = data['current']['humidity']

    # Send data to sheets
    wks.append_row([api_time, sensor_temperature,
                   sensor_humidity, api_temp, api_humidity])

    # Wait for 15 minutes
    time.sleep(900)
