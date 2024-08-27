# libraries
import Adafruit_DHT
import time
import requests
import json
import pandas as pd
import gspread
import RPi.GPIO as GPIO
import requests
from datetime import datetime, timedelta
from send_notif import send_pushover_notification

# setting up google sheets
sa = gspread.service_account(
    filename='sensing-and-iot-project-697ae27b6369.json')

sh = sa.open("Sensing IoT Data")

wks = sh.worksheet("Actuation")



# Sensor setup
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4

# Define the pin numbers for the LEDs
BLUE_LED_PIN = 12
RED_LED_PIN = 13

# Set the GPIO mode
GPIO.setmode(GPIO.BCM)

# Set up the LED pins for output
GPIO.setup(RED_LED_PIN, GPIO.OUT)
GPIO.setup(BLUE_LED_PIN, GPIO.OUT)


def round_time(dt, round_to=15):
    # Round a datetime object to any time lapse in minutes
    minutes = dt.minute
    rounding = (minutes + round_to / 2) // round_to * round_to
    return dt + timedelta(minutes=rounding - minutes) - timedelta(seconds=dt.second, microseconds=dt.microsecond)


# Initialize dataframe
df = pd.DataFrame(columns=['Time', 'Sensor Temp (°C)', 'Sensor Humidity (%)'])

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

    # Get current local time
    current_time = datetime.now()
    # Round to the nearest 15 minutes
    rounded_time = round_time(current_time)
    rounded_time_str = rounded_time.strftime('%Y-%m-%d %H:%M:%S')

    # Send data to sheets
    wks.append_row([rounded_time_str, sensor_temperature, sensor_humidity])

    # Ensures all LEDs are off
    GPIO.output(RED_LED_PIN, GPIO.LOW)
    GPIO.output(BLUE_LED_PIN, GPIO.LOW)

    if sensor_temperature > 21 and sensor_humidity > 60:
        # Ensures only red LED is on
        GPIO.output(RED_LED_PIN, GPIO.HIGH)
        GPIO.output(BLUE_LED_PIN, GPIO.LOW)

        message = "Temperature and humidity are getting above ideal range - Turn heating off, open the windows and turn the fans on"

        result = send_pushover_notification(message)
        print(result)

    elif sensor_temperature > 21:
        # Ensures only red LED is on
        GPIO.output(RED_LED_PIN, GPIO.HIGH)
        GPIO.output(BLUE_LED_PIN, GPIO.LOW)

        message = "Temperature is getting above ideal range - Turn heating off"

        result = send_pushover_notification(message)
        print(result)

    elif sensor_humidity > 60:
        # Ensures only red LED is on
        GPIO.output(RED_LED_PIN, GPIO.HIGH)
        GPIO.output(BLUE_LED_PIN, GPIO.LOW)

        message = "Humidity is getting above ideal range - Turn fans on and open windows"

        result = send_pushover_notification(message)
        print(result)

    elif sensor_temperature < 18 and sensor_humidity < 40:
        # Ensures only blue LED is on
        GPIO.output(RED_LED_PIN, GPIO.LOW)
        GPIO.output(BLUE_LED_PIN, GPIO.HIGH)

        message = "Temperature and humidity are getting below ideal range - Turn heating on"

        result = send_pushover_notification(message)
        print(result)

    elif sensor_temperature < 18:
        # Ensures only blue LED is on
        GPIO.output(RED_LED_PIN, GPIO.LOW)
        GPIO.output(BLUE_LED_PIN, GPIO.HIGH)

        message = "Temperature is getting below ideal range - Turn heating on"

        result = send_pushover_notification(message)
        print(result)

    elif sensor_humidity < 40:
        # Ensures only blue LED is on
        GPIO.output(RED_LED_PIN, GPIO.LOW)
        GPIO.output(BLUE_LED_PIN, GPIO.HIGH)

        message = "Humidity is getting below ideal range - No suitable actuations as of yet"

        result = send_pushover_notification(message)
        print(result)

    else:
        # Ensures all LEDs are off
        GPIO.output(RED_LED_PIN, GPIO.LOW)
        GPIO.output(BLUE_LED_PIN, GPIO.LOW)

    # Wait for 15 minutes
    time.sleep(900)
