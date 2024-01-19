import scenario as sn
import math
import numpy as np
import pandas as pd
from itertools import product

# * parsing argomenti e documentazione
import sys

args = sys.argv

if len(args) < 5:
    print("Numero di argomenti non valido")
    exit(1)
if args[-1] == "--h":
    print("blender [-b] -P scan.py <csv_file> <label>")
    print(
        "Esegue la simulazione con una data traiettoria; salva i file csv risultanti nella cartella './scans/csv'"
    )
    print("csv_file: file csv contenente la traiettoria")
    print("label: label della traiettoria")
    print("-b: esegue lo script in background")
    print("-P --python: esegue lo script Python")
    exit(0)

csv_file = args[-2].replace("\\", "/")
label = args[-1].replace("\\", "/")

vehicle_loc_rot = pd.read_csv(f"{csv_file}")
labels = vehicle_loc_rot["label"].unique()

trajectory = vehicle_loc_rot[vehicle_loc_rot["label"] == label].reset_index(drop=True)
print(trajectory)
n_frame = len(trajectory)

# * carico la ford thunderbird 1961 nella scena
vehicle_data = [
    ("assets/ford.obj", trajectory, "vehicle1", "vehicle1"),
    # aggiungi tutti i veicoli della scena a questo array
]
vehicles = [sn.Vehicle(*data) for data in vehicle_data]

scene = sn.Scene(vehicles)

# * Calcola i limiti delle traiettorie
min_x = abs(min(min(vehicle.keyframes["x"]) for vehicle in vehicles))
max_x = abs(max(max(vehicle.keyframes["x"]) for vehicle in vehicles))
min_y = abs(min(min(vehicle.keyframes["y"]) for vehicle in vehicles))
max_y = abs(max(max(vehicle.keyframes["y"]) for vehicle in vehicles))

sensor_distance = np.ceil(max(min_x, max_x, min_y, max_y))
sensor_loc_rot = pd.read_csv("sensor_keyframes.csv")
# Crea e posiziona i sensori intorno al centro del quadrato
for i, (dx, dy) in enumerate(product([-1, 1], repeat=2)):
    sensor_x = dx * sensor_distance / 2
    sensor_y = dy * sensor_distance / 2
    sensor_heading = None
    if sensor_x < 0:
        sensor_heading = (math.radians(90), 0, math.radians(-90))
    else:
        sensor_heading = (math.radians(90), 0, math.radians(90))

    sensor = sn.Sensor(
        position=(sensor_x, sensor_y, 3.5),
        heading=sensor_heading,  # Impostare l'orientamento desiderato
        name=f"camera_{i}",
        data=f"scan_camera_{i}.csv",
    )
    scene.add_sensor(sensor)

scene.build()

for i in range(1):
    scene.scan(i)
    scene.update()
