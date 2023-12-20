import bpy
from bpy import data as D
from bpy import context as C
from mathutils import *
from math import *
import blensor
import json
import numpy as np
import pandas as pd

# * eseguire il comando "blender -P scan.py" per aprire blender e eseguire lo script
# * eseguire il comando "blender -b -P scan.py" per eseguire lo script in background


class Vehicle:
    def __init__(self, model, keyframes, name, data, sensors=[]):
        self.model = model
        self.keyframes = keyframes
        self.sensors = sensors
        self.name = name

        # posizione e direzione iniziale
        self.position = (self.keyframes["x"][79], self.keyframes["y"][79], 1.0)
        self.heading = (0, 0, self.keyframes["heading"][0])

    # scrivi le funzioni per muovere la macchina
    def move(self, position, heading):
        self.position = position
        self.heading = heading


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

    def scan(self):
        with open("data.json", "r") as file:
            data = json.load(file)

        for sensor in self.sensors:
            current_sensor = bpy.data.objects[sensor.name]
            bpy.context.scene.camera = current_sensor

            rotation_scan_x = Matrix.Rotation(sensor.rotation_euler[0], 4, "X")
            rotation_scan_y = Matrix.Rotation(sensor.rotation_euler[1], 4, "Y")
            rotation_scan_z = Matrix.Rotation(sensor.rotation_euler[2], 4, "Z")

            total_rotation = rotation_scan_z * rotation_scan_y * rotation_scan_x

            blensor.blendodyne.scan_advanced(
                current_sensor,
                rotation_speed=10.0,
                simulation_fps=24,
                angle_resolution=0.1728,
                max_distance=100,
                evd_file=f"{sensor.name}.numpy",
                noise_mu=0.0,
                noise_sigma=0.03,
                start_angle=-90.0,
                end_angle=90.0,
                evd_last_scan=True,
                add_blender_mesh=False,
                add_noisy_blender_mesh=False,
                world_transformation=total_rotation,
            )

            scan = np.loadtxt(f"{sensor.name}00000.numpy")
            rounded_scan = np.round(scan, decimals=3)

            filtered = rounded_scan[rounded_scan[:, 7] != -3.2]

            df = pd.DataFrame(filtered, columns=data["columns"])
            df.to_csv(f"{sensor.name}.csv", index=False)


loc_rot = pd.read_csv("keyframes.csv")
labels = loc_rot["label"].unique()

trajectory_1 = loc_rot[loc_rot["label"] == labels[0]].reset_index(drop=True)
trajectory_2 = loc_rot[loc_rot["label"] == labels[1]].reset_index(drop=True)

# * carico la ford thunderbird 1961 nella scena
vehicle_1 = Vehicle("assets/ford.obj", trajectory_1, "vehicle1", "vehicle1")
vehicle_2 = Vehicle("assets/ford.obj", trajectory_2, "vehicle2", "vehicle2")
vehicles = [vehicle_1, vehicle_2]
scene = Scene(vehicles)

# * aggiungo le 4 camere esterne nella scena
# for i in range(4):
#     sensor = scene.Sensor(
#         position = (loc_rot[f"camera_{i}_position"][0], loc_rot[f"camera_{i}_position"][1], loc_rot[f"camera_{i}_position"][2]),
#         heading = (math.radians( loc_rot[f"camera_{i}_rotation"][0] ), math.radians( loc_rot[f"camera_{i}_rotation"][1] ), math.radians( loc_rot[f"camera_{i}_rotation"][2] )),
#         keyframes = loc_rot,
#         name = f"camera_{i}",
#         data = f"scan_camera_{i}.csv"
#     )
#     scene.add_sensor(sensor)
scene.build()

# * Modello Ford Thunderbird 1961
# car_model =  "assets/car.obj"

# * definisce posizioni e rotazioni della macchina e della camera
# loc_rot = pd.read_csv("keyframes.csv")

# * Carica il modello della macchina nella scena
# bpy.ops.import_scene.obj(filepath=car_model)


# * Posiziona la macchina nella scena (esempio: posizioniamola a X=0, Y=0, Z=0)
# car_object = bpy.context.selected_objects[0]  # Seleziona il primo oggetto importato (la macchina)
# car_object.location = (loc_rot["car_position"][0], loc_rot["car_position"][1], loc_rot["car_position"][2])  # Imposta la posizione desiderata
# car_object.rotation_euler = ( math.radians( loc_rot["car_rotation"][0] ), math.radians( loc_rot["car_rotation"][1] ), math.radians( loc_rot["car_rotation"][2] ) )

# * Crea un cubo, un ostacolo per le prove dei sensori
# bpy.ops.mesh.primitive_cube_add(radius = 1.0, location = (0,0,1.3), rotation = (0,0,0))

# * Aggiungi le 4 camere nella scena
# for i in range(4):
#     bpy.ops.object.camera_add(
#         location=(
#             loc_rot[f"camera_{i}_position"][0],
#             loc_rot[f"camera_{i}_position"][1],
#             loc_rot[f"camera_{i}_position"][2]
#         ),
#         rotation=(
#             math.radians( loc_rot[f"camera_{i}_rotation"][0] ),
#             math.radians( loc_rot[f"camera_{i}_rotation"][1] ),
#             math.radians( loc_rot[f"camera_{i}_rotation"][2] )
#         )
#     )  # Imposta la posizione della camera
#     camera_corrente = bpy.context.object
#     #* rinomina la camera e i dati della camera
#     camera_corrente.name = f"camera_{i}"
#     camera_corrente.data.name = f"Camera_{i}_Data"


# * Crea un piano (superficie piana), assimilabile alla strada
# bpy.ops.mesh.primitive_plane_add(radius=10.0, location=(0,0,0.3), rotation=(0,0,0))
# plane = bpy.data.objects["Plane"]

# * Crea un cubo, un ostacolo per le prove dei sensori
# bpy.ops.mesh.primitive_cube_add(radius = 1.0, location = (-1.0, 10.0, 1.3), rotation = (0,0,0))

# * prende le colonne dal file data.json
# with open('data.json', 'r') as file:
#     data = json.load(file)

# #* eseguo una scansione con ogni camera. Una per volta
# for i in range(4):
#     #* attivo la camera "camera_i"
#     camera = bpy.data.objects[f"camera_{i}"]
#     bpy.context.scene.camera = camera


#     rotation_scan_x = Matrix.Rotation(camera.rotation_euler[0], 4, 'X')
#     rotation_scan_y = Matrix.Rotation(camera.rotation_euler[1], 4, 'Y')
#     rotation_scan_z = Matrix.Rotation(camera.rotation_euler[2], 4, 'Z')


#     # ottiei total_rotation in un altro modo (non funziona)
#     # non usare l'operatore @, ma il metodo .multiply()
#     total_rotation = rotation_scan_z * rotation_scan_y * rotation_scan_x


#     #* I punti della scansione vengono calolati in modo assoluto rispetto alla scena
#     #* local_coordinates = False allora i punti della scansione vengono calcolati in modo assoluto
#     # local_coordinates = True allora i punti della scansione vengono calcolati in modo relativo alla camera
#     blensor.blendodyne.scan_advanced(camera, rotation_speed = 10.0,
#                                    simulation_fps=24, angle_resolution = 0.1728,
#                                    max_distance = 100, evd_file= f"scan_camera_{i}.numpy",
#                                    noise_mu=0.0, noise_sigma=0.03, start_angle = -90.0,
#                                    end_angle = 90.0, evd_last_scan=True,
#                                    add_blender_mesh = False,
#                                    add_noisy_blender_mesh = False,
#                                    world_transformation=total_rotation)

#     scan = np.loadtxt(f"scan_camera_{i}00000.numpy")
#     rounded_scan = np.round(scan, decimals=3)

#     #* filtro i punti dello scan on z = 0.3 (pavimento), per eliminare i punti che intersecano la strada
#     filtered = rounded_scan[rounded_scan[:,7] != -3.2]

#     #* crea un dataframe pandas con tutti i punti filtrati
#     df = pd.DataFrame(filtered, columns=data['columns'])
#     df.to_csv(f"scan_camera_{i}.csv", index=False)

# * la distanza è calcolata con: coordinata ostacolo - coordinata camera
# * le distanze sono ricavate con la formula: coordinata camera - coordinata ostcolo senza fare il modulo
