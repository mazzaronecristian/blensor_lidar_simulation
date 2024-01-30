import bpy
import blensor
import json
from mathutils import *
import math
from math import *
import numpy as np
import pandas as pd

# import scenario as sn

class Vehicle:
    def __init__(self, model, keyframes, name, sensors=[]):
        self.model = model
        self.keyframes = keyframes
        self.sensors = sensors
        self.name = name
        self.current_step = 0

        # * posizione e direzione iniziale
        self.position = (
            self.keyframes["x"][self.current_step],
            self.keyframes["y"][self.current_step],
            0.3,
        )
        # * i modelli vengono ruotati di -90 gradi attorno a x di default. Per questo motivo aggiungo 90 gradi
        self.heading = (
            math.radians(90),
            0,
            self.keyframes["heading"][self.current_step],
        )

    def add_sensor(self, sensor):
        self.sensors.append(sensor)
    def move(self, position, heading):
        self.position = position
        self.heading = heading

    def move(self):
        self.current_step += 1
        if self.current_step >= len(self.keyframes["x"]):
            return
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
        if self.sensors == []:
            return
        for sensor in self.sensors:
            if hasattr(sensor, "move") and callable(getattr(sensor, "move")):
                sensor.move(
                    position=(
                        self.keyframes["x"][self.current_step],
                        self.keyframes["y"][self.current_step],
                        sensor.position[2],
                    ),
                    heading=(
                        math.radians(90),
                        0,
                        math.radians(-90)
                        + self.keyframes["heading"][self.current_step],
                    ),
                )


class Sensor:
    def __init__(self, position, heading, name, data):
        self.position = position
        self.heading = heading
        self.name = name
        self.data = data

    def move(self, position, heading):
        self.position = position
        self.heading = heading


class Scene:
    def __init__(self, vehicles=[], sensors=[], center = {"x": 0, "y": 0, "z": 0}):
        self.vehicles = vehicles
        self.sensors = sensors
        self.center = center
        self.center["z"] += 0.3

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
            radius=10.0, location=(self.center["x"],self.center["y"],self.center["z"] ), rotation=(0, 0, 0)
        )
        bpy.context.object.name = "Plane"
        bpy.context.object.data.name = "Plane_Data"
        bpy.data.objects["Plane"].scale = (10, 10, 10)
        # carica tutti i veicoli nella scena
        for vehicle in self.vehicles:
            bpy.ops.import_scene.obj(filepath=vehicle.model)
            car_object = bpy.context.selected_objects[0]
            car_object.location = vehicle.position
            car_object.rotation_euler = vehicle.heading
            car_object.name = vehicle.name
            car_object.data.name = f"{vehicle.name}_Data"

        # * carica tutti i sensori nella scena
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
            for sensor in vehicle.sensors:
                if (
                    hasattr(sensor, "name")
                    and hasattr(sensor, "position")
                    and hasattr(sensor, "heading")
                ):
                    current_sensor = bpy.data.objects[sensor.name]
                    current_sensor.location = sensor.position
                    current_sensor.rotation_euler = sensor.heading

    # esegui un refactoring del codice per eliminare la ripetizione di codice

    # * esegue una scansione e salva i dati in scans/csv/{sensor.name}_{i}.csv e scans/numpy/{sensor.name}_{i}.numpy
    def scan(self, i=None, filter=False):
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
                start_angle=0,
                end_angle=360,
                evd_last_scan=True,
                add_blender_mesh=False,
                add_noisy_blender_mesh=False,
                world_transformation=total_rotation,
            )
            evd_filename += f"00000.numpy"
            scan = np.loadtxt(evd_filename)
            rounded_scan = np.round(scan, decimals=3)

            # * filtro i dati per eliminare la "strada"
            pavement = bpy.data.objects["Plane"].location.z
            height = current_sensor.location.z

            if filter:
                rounded_scan = rounded_scan[
                    rounded_scan[:, 7] != np.round(pavement - height, decimals=3)
                ]

            df = pd.DataFrame(rounded_scan, columns=data["columns"])
            df.to_csv(csv_filename, index=False)


def filter_pavement(point_cloud, pavement_height, sensor_height):
    return point_cloud[
        point_cloud[:, 7] != np.round(pavement_height - sensor_height, decimals=3)
    ]
