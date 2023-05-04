import time
from plant_monitor import PlantMonitor

monitor = PlantMonitor()

while True:
    wetness.value = str(monitor.get_wetness())
    temp.value = str(monitor.get_temp())
    humidity.value = str(monitor.get_humidity())
    time.sleep(2)
