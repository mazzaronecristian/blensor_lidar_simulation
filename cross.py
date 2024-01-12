import scenario as sn
import pandas as pd
import numpy as np
import math

# TODO: script per la creazione simulazione con veicoli e sensori (solidali ai veicoli) e traiettorie 1 e 3
trajecoties = pd.read_csv("vehicle_keyframes.csv")

labels = trajecoties["label"].unique()

# * traiettoria della macchina
trajectory_1 = trajecoties[trajecoties["label"] == "Trajectory_1"].reset_index(
    drop=True
)

# * traiettoria dell'autobus
trajectory_3 = trajecoties[trajecoties["label"] == "Trajectory_3"].reset_index(
    drop=True
)

sensor_ford = sn.Sensor(
    position=(trajectory_1["x"][0], trajectory_1["y"][0], 3.5),
    heading=(
        math.radians(90),
        0,
        trajectory_1["heading"][0],
    ),
    name="camera_ford",
    data="scan_camera_ford.csv",
)

sensor_autobus = sn.Sensor(
    position=(trajectory_3["x"][0], trajectory_3["y"][0], 3.5),
    heading=(
        math.radians(90),
        0,
        trajectory_3["heading"][0],
    ),
    name="camera_autobus",
    data="scan_camera_autobus.csv",
)

vehicles_data = [
    (
        "assets/ford.obj",
        trajectory_1,
        "vehicle1",
        [sensor_ford],
    ),
    (
        "assets/bus.obj",
        trajectory_3,
        "vehicle2",
        [sensor_autobus],
    ),
]
vehicles = [sn.Vehicle(*data) for data in vehicles_data]

scene = sn.Scene(vehicles)
