import bpy
from bpy import data as D
from bpy import context as C
import blensor
import json
from mathutils import *
import math
from math import *
import numpy as np
import pandas as pd

# import scenario as sn


class Vehicle:
    def __init__(self, model, keyframes, name, data, sensors=[]):
        self.model = model
        self.keyframes = keyframes
        self.sensors = sensors
        self.name = name
        self.current_step = 0

        # * posizione e direzione iniziale
        self.position = (
            # self.keyframes["x"][self.current_step],
            # self.keyframes["y"][self.current_step],
            # 0.3,
            -22.05,
            -29.7,
            0.7,
        )
        # * i modelli vengono ruotati di -90 gradi attorno a x di default. Per questo motivo aggiungo 90 gradi
        self.heading = (
            math.radians(90),
            0,
            self.keyframes["heading"][self.current_step],
        )

    def move(self, position, heading):
        self.position = position
        self.heading = heading

    def move(self):
        self.current_step += 1
        self.position = (
            self.keyframes["x"][self.current_step],
            self.keyframes["y"][self.current_step],
            1.0,
        )
        self.heading = (
            math.radians(90),
            0,
            self.keyframes["heading"][self.current_step],
        )


class Sensor:
    def __init__(self, position, heading, keyframes, name, data, trajectory=None):
        self.position = position
        self.heading = heading
        self.keyframes = keyframes
        self.trajectory = trajectory
        self.name = name
        self.data = data

    def move(self, position, heading):
        if self.trajectory is not None:
            self.position = position
            self.heading = heading


class Scene:
    def __init__(self, vehicles=[], sensors=[]):
        self.vehicles = vehicles
        self.sensors = sensors

        bpy.ops.mesh.primitive_plane_add(
            radius=10.0, location=(0, 0, 0.3), rotation=(0, 0, 0)
        )
        self.plane = bpy.data.objects["Plane"]

    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)

    def add_sensor(self, sensor):
        self.sensors.append(sensor)

    def clean(self):
        # * Elimina tutti gli oggetti nella scena
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete()

    def build(self):
        self.clean()

        # * carico un pavimento di prova
        bpy.ops.mesh.primitive_plane_add(
            radius=10.0, location=(0, 0, 0.3), rotation=(0, 0, 0)
        )
        bpy.context.object.name = "Plane"
        bpy.context.object.data.name = "Plane_Data"
        bpy.data.objects["Plane"].scale = (4, 4, 4)
        # carica tutti i veicoli nella scena
        for vehicle in self.vehicles:
            bpy.ops.import_scene.obj(filepath=vehicle.model)
            car_object = bpy.context.selected_objects[0]
            car_object.location = vehicle.position
            car_object.rotation_euler = vehicle.heading
            car_object.name = vehicle.name
            car_object.data.name = f"{vehicle.name}_Data"

        # carica tutti i sensori nella scena
        for sensor in self.sensors:
            bpy.ops.object.camera_add(location=sensor.position, rotation=sensor.heading)
            current_sensor = bpy.context.object
            current_sensor.name = sensor.name
            current_sensor.data.name = f"{sensor.name}_Data"

    def update(self):
        for vehicle in self.vehicles:
            vehicle.move()
            car_object = bpy.data.objects[vehicle.name]
            car_object.location = vehicle.position
            car_object.rotation_euler = vehicle.heading

    # esegui un refactoring del codice per eliminare la ripetizione di codice

    # * esegue una scansione e salva i dati in scans/csv/{sensor.name}_{i}.csv e scans/numpy/{sensor.name}_{i}.numpy
    def scan(self, i=None):
        with open("data.json", "r") as file:
            data = json.load(file)

        for sensor in self.sensors:
            current_sensor = bpy.data.objects[sensor.name]
            bpy.context.scene.camera = current_sensor

            # * calcolo la matrice di rotazione totale del sensore
            rotation_scan_x = Matrix.Rotation(current_sensor.rotation_euler[0], 4, "X")
            rotation_scan_y = Matrix.Rotation(current_sensor.rotation_euler[1], 4, "Y")
            rotation_scan_z = Matrix.Rotation(current_sensor.rotation_euler[2], 4, "Z")

            total_rotation = rotation_scan_z * rotation_scan_y * rotation_scan_x

            evd_filename = f"scans/numpy/{sensor.name}"
            csv_filename = f"scans/csv/{sensor.name}"

            if i is not None:
                evd_filename += f"_{i}_"
                csv_filename += f"_{i}"

            csv_filename += ".csv"

            # * eseguo la scansione
            blensor.blendodyne.scan_advanced(
                current_sensor,
                rotation_speed=10.0,
                simulation_fps=24,
                angle_resolution=0.1728,
                max_distance=150,
                evd_file=f"{evd_filename}.numpy",
                noise_mu=0.0,
                noise_sigma=0.03,
                start_angle=-90.0,
                end_angle=90.0,
                evd_last_scan=True,
                add_blender_mesh=False,
                add_noisy_blender_mesh=False,
                world_transformation=total_rotation,
            )
            evd_filename += f"00000.numpy"
            scan = np.loadtxt(evd_filename)
            rounded_scan = np.round(scan, decimals=3)

            # TODO: Rivedere il filtro dei punti per eliminare il pavimento
            filtered = rounded_scan[rounded_scan[:, 7] != -3.2]

            df = pd.DataFrame(filtered, columns=data["columns"])
            df.to_csv(csv_filename, index=False)


def center_trajectory(trajectory):
    x_coords = trajectory["x"]
    y_coords = trajectory["y"]

    centroid_x = np.mean(x_coords)
    centroid_y = np.mean(y_coords)

    translation_x = -centroid_x
    translation_y = -centroid_y

    x_coords_trasl = x_coords + translation_x
    y_coords_trasl = y_coords + translation_y

    trajectory["x"] = x_coords_trasl
    trajectory["y"] = y_coords_trasl


# * eseguire il comando "blender -P scan.py" per aprire blender e eseguire lo script
# * eseguire il comando "blender -b -P scan.py" per eseguire lo script in background

vehicle_loc_rot = pd.read_csv("vehicle_keyframes.csv")
labels = vehicle_loc_rot["label"].unique()

trajectory_1 = vehicle_loc_rot[vehicle_loc_rot["label"] == labels[0]].reset_index(
    drop=True
)
n_frame = len(trajectory_1)

# trajectory_2 = vehicle_loc_rot[vehicle_loc_rot["label"] == labels[1]].reset_index(
#     drop=True
# )

# * centro la traiettoria rispetto al sistema di riferimento dello scenario
center_trajectory(trajectory_1)

# * carico la ford thunderbird 1961 nella scena
vehicle_data = [
    ("assets/ford.obj", trajectory_1, "vehicle1", "vehicle1"),
    # ("assets/bus.obj", trajectory_2, "vehicle2", "vehicle2")
]

vehicles = [Vehicle(*data) for data in vehicle_data]

scene = Scene(vehicles)


sensor_loc_rot = pd.read_csv("sensor_keyframes.csv")
n_sensor = len(sensor_loc_rot)

for i in range(n_sensor):
    sensor = Sensor(
        position=(
            sensor_loc_rot["x"][i],
            sensor_loc_rot["y"][i],
            sensor_loc_rot["z"][i],
        ),
        heading=(
            math.radians(sensor_loc_rot["x_rotation"][i]),
            math.radians(sensor_loc_rot["y_rotation"][i]),
            math.radians(sensor_loc_rot["z_rotation"][i]),
        ),
        keyframes=sensor_loc_rot,
        name=f"camera_{i}",
        data=f"scan_camera_{i}.csv",
    )
    scene.add_sensor(sensor)

scene.build()

for i in range(1):
    scene.scan(i)
    scene.update()
