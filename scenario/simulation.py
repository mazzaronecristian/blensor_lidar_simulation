import bpy
import blensor
import json
from mathutils import *
import math
from math import *
import numpy as np
import pandas as pd


class Static_object:
    def __init__(self, model, position, heading, name):
        self.model = model
        self.position = position
        self.heading = heading
        self.name = name


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


class SceneBuilder:
    def __init__(self):
        self.scene = Scene()

    def with_vehicles(self, vehicles):
        self.scene.vehicles = vehicles
        return self

    def with_sensors(self, sensors):
        self.scene.sensors = sensors
        return self

    def with_center(self, center):
        center["z"] += 0.3
        self.scene.center = center
        return self

    def with_static_objects(self, static_objects):
        self.scene.static_objects = static_objects
        return self

    def build(self) -> "Scene":
        return self.scene


class Scene:
    """
    Represents a scene in the simulation.

    Attributes:
        center (dict): The center coordinates of the scene.
        vehicles (list): List of vehicles in the scene.
        sensors (list): List of sensors in the scene.
        static_objects (list): List of static objects in the scene.
    """

    def __init__(self):
        self.center = {"x": 0, "y": 0, "z": 0.3}
        self.vehicles = []
        self.sensors = []
        self.static_objects = []

    def add_vehicle(self, vehicle):
        """
        Adds a vehicle to the scene.

        Args:
            vehicle (Vehicle): The vehicle object to add.
        """
        self.vehicles.append(vehicle)

    def add_sensor(self, sensor):
        """
        Adds a sensor to the scene.

        Args:
            sensor (Sensor): The sensor object to add.
        """
        self.sensors.append(sensor)

    def clean(self):
        """
        Cleans the scene by deleting all objects.
        """
        # * Elimina tutti gli oggetti nella scena
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete()

    def _load_objects(self):
        """
        Loads the vehicles, sensors, and static objects into the scene.
        """
        for vehicle in self.vehicles:
            bpy.ops.import_scene.obj(filepath=vehicle.model)
            car_object = bpy.context.selected_objects[0]
            car_object.location = vehicle.position
            car_object.rotation_euler = vehicle.heading
            car_object.name = vehicle.name
            car_object.data.name = f"{vehicle.name}_Data"

        for sensor in self.sensors:
            bpy.ops.object.camera_add(location=sensor.position, rotation=sensor.heading)
            current_sensor = bpy.context.object
            current_sensor.name = sensor.name
            current_sensor.data.name = f"{sensor.name}_Data"

        for static_object in self.static_objects:
            if not hasattr(static_object, "model"):
                continue
            bpy.ops.import_scene.obj(filepath=static_object.model)
            static_object = bpy.context.selected_objects[0]
            static_object.location = static_object.position
            static_object.rotation_euler = static_object.heading
            static_object.name = static_object.name
            static_object.data.name = f"{static_object.name}_Data"

    def load(self):
        """
        Loads the scene by creating a plane and loading objects into it.
        """
        self.clean()

        bpy.ops.mesh.primitive_plane_add(
            radius=10.0,
            location=(self.center["x"], self.center["y"], self.center["z"]),
            rotation=(0, 0, 0),
        )
        bpy.context.object.name = "Plane"
        bpy.context.object.data.name = "Plane_Data"
        bpy.data.objects["Plane"].scale = (10, 10, 10)

        self._load_objects()

    def update(self):
        """
        Updates the positions and orientations of vehicles and sensors in the scene.
        """
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

    def scan(self, i=None, filter=False):
        """
        Performs a scan using the sensors in the scene and saves the data.

        Args:
            i (int, optional): The index of the scan. Defaults to None.
            filter (bool, optional): Whether to filter the data. Defaults to False.
        """
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
