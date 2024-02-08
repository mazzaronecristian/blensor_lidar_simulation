import pandas as pd
import scenario as sn
import math

# TODO: Modificare lo script per poter assegnare i sensori a un veicolo a seconda di quanto scritto nel file delle posizioni dei sensori

import sys

args = sys.argv
args = args[args.index("--") + 1 :]  # get all args after "--"
if len(args) == 3 or len(args) < 2 and args[-1] != "h":
    print("Numero di argomenti non valido")
    exit(1)
if args[-1] == "h":
    print(
        "blender [-b] -P run_simulation.py -- <vehicles_traj> <sensors_pos> [<center_x>] [<center_y>]"
    )
    print(
        "Esegue la simulazione con una data traiettoria; salva i file csv risultanti nella cartella './scans/csv'"
    )
    print(
        "--:          Blender ignora tutti gli argomenti dopo => inserire gli argomenti dello script PYTHON dopo --"
    )
    print("vehicles_traj:    file csv contenente le traiettorie")
    print("sensors_pos:       file csv contenente le posizioni dei sensori")
    print("center_x:       coordinata x del centro della simulazione")
    print("center_y:       coordinata y del centro della simulazione")
    print("-b:          esegue lo script in background")
    print("-P --python: esegue lo script Python")
    exit(0)

if len(args) == 4:
    center_x = int(args[-2])
    center_y = int(args[-1])
else:
    center_x = 0
    center_y = 0

vehicles_traj = args[0].replace("\\", "/")
sensors_pos = args[1].replace("\\", "/")

vehicle_loc_rot = pd.read_csv(f"{vehicles_traj}")
labels = vehicle_loc_rot["label"].unique()

vehicles_data = {key: "" for key in labels}

n_frame = 0
for label in labels:
    trajectory = vehicle_loc_rot[vehicle_loc_rot["label"] == label].reset_index(
        drop=True
    )
    if len(trajectory) > n_frame:
        n_frame = len(trajectory)
    if trajectory.at[0, "object_type"] == "vehicle":
        vehicles_data[label] = ("assets/ford.obj", trajectory, label, label)
    if trajectory.at[0, "object_type"] == "bus":
        vehicles_data[label] = ("assets/bus.obj", trajectory, label, label)
    if trajectory.at[0, "object_type"] == "motorcycle":
        vehicles_data[label] = ("assets/motorcycle.obj", trajectory, label, label)

vehicles = [sn.Vehicle(*data) for data in vehicles_data.values()]

sensors_data = []
sensor_loc = pd.read_csv(f"{sensors_pos}")
for i, sensor in enumerate(sensor_loc.iloc):
    sensors_data.append(
        (
            (sensor.x, sensor.y, sensor.z),
            (
                math.radians(sensor.x_rotation),
                math.radians(sensor.y_rotation),
                math.radians(sensor.z_rotation),
            ),
            f"sensor_{i}",
            f"scan_sensor_{i}.csv",
        )
    )
sensors = [sn.Sensor(*data) for data in sensors_data]
scene = (
    sn.SceneBuilder()
    .with_vehicles(vehicles)
    .with_sensors(sensors)
    .with_center({"x": center_x, "y": center_y, "z": 0})
    .build()
)
scene.load()

for i in range(0):
    scene.scan(i)
    scene.update()
