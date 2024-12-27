import time, os
import datetime
from sds011 import SDS011
import aqi
from metrics_handler import *

DEV_PATH = '/dev/ttyUSB0'

def mesure():
    sensor = SDS011(DEV_PATH, use_query_mode=True)
    print('Sleep device...')
    sensor.sleep(sleep=True)  # Turn off fan and diode
    print('Wake-up device...')
    sensor.sleep(sleep=False)  # Turn on fan and diode
    print('Mesure for 30 secs...')
    time.sleep(30)  # Allow time for the sensor to measure properly
    print('Query data...')
    result = sensor.query()
    print('Sleep device...')
    sensor.sleep()  # Turn off fan and diode
    return result if result else (0, 0)

def generate_metrics():
    pm25, pm10 = mesure()
    aqi_calculate = int(aqi.to_aqi([
        (aqi.POLLUTANT_PM25, pm25),
        (aqi.POLLUTANT_PM10, pm10),
    ]))
    print('Result: AQI: {}, PM2.5: {}, PM10: {}'.format(aqi_calculate, pm25, pm10))
    metrics = f"""     
# HELP temperature Measured temperature in Celsius
# TYPE temperature gauge
pm2_5 {pm25}
# HELP rh_data Relative humidity data as a percentage
# TYPE rh_data gauge
pm10 {pm10}
# HELP co2 Carbon dioxide concentration in ppm
# TYPE co2 gauge
aqi {aqi_calculate}
"""
    return metrics


if __name__ == '__main__':
    if os.geteuid() != 0:
        exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.")
    server_address = ("0.0.0.0", 8010) 
    httpd = HTTPServer(server_address, MetricsHandler)
    print(f"Serving metrics on http://localhost:8010/metrics")
    httpd.serve_forever()
