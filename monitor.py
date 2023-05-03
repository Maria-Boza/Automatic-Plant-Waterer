import threading
import time
from plant_monitor import PlantMonitor

monitor = PlantMonitor()

def update_readings():
    while True:
        wetness.value = str(monitor.get_wetness())
        temp.value = str(monitor.get_temp())
        humidity.value = str(monitor.get_humidity())
        time.sleep(2)

update_readings()
