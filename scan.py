import scenario as sn
import math
import numpy as np
import pandas as pd
from itertools import product

# * eseguire il comando "blender -P scan.py" per aprire blender e eseguire lo script
# * eseguire il comando "blender -b -P scan.py" per eseguire lo script in background

vehicle_loc_rot = pd.read_csv("vehicle_keyframes.csv")
labels = vehicle_loc_rot["label"].unique()

trajectory = vehicle_loc_rot[vehicle_loc_rot["label"] == "Trajectory_1"].reset_index(
    drop=True
)
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

for i in range(n_frame):
    scene.scan(i)
    scene.update()
