import scenario as sn
import pandas as pd
import math

trajecoties = pd.read_csv("cross_trajectories.csv")

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
        math.radians(-90) + trajectory_1["heading"][0],
    ),
    name="camera_ford",
    data="scan_camera_ford.csv",
)

sensor_autobus = sn.Sensor(
    position=(trajectory_3["x"][0], trajectory_3["y"][0], 6),
    heading=(
        math.radians(90),
        0,
        math.radians(-90) + trajectory_3["heading"][0],
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

scene = sn.Scene(vehicles, sensors=[sensor_ford, sensor_autobus])
scene.load()

# * n_frame è uguale al numero di frame della traiettoria più corta
n_frame = min(len(trajectory_1), len(trajectory_3))
for i in range(n_frame):
    scene.scan(i)
    scene.update()
