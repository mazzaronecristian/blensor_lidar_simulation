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


with open("data.json", "r") as file:
    data = json.load(file)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(math.radians(60), 0, 0))
current_sensor = bpy.context.object
bpy.context.scene.camera = current_sensor

rotation_scan_x = Matrix.Rotation(current_sensor.rotation_euler[0], 4, "X")
rotation_scan_y = Matrix.Rotation(current_sensor.rotation_euler[1], 4, "Y")
rotation_scan_z = Matrix.Rotation(current_sensor.rotation_euler[2], 4, "Z")

total_rotation = rotation_scan_z * rotation_scan_y * rotation_scan_x

bpy.ops.surface.primitive_nurbs_surface_sphere_add(radius=2, location=(0, 6, -7))
bpy.context.object.name = "sphere"

blensor.blendodyne.scan_advanced(
    current_sensor,
    rotation_speed=10.0,
    simulation_fps=24,
    angle_resolution=0.1728,
    max_distance=300,
    evd_file="scan_sphere.numpy",
    noise_mu=0.0,
    noise_sigma=0.03,
    start_angle=0,
    end_angle=360,
    evd_last_scan=True,
    add_blender_mesh=False,
    add_noisy_blender_mesh=False,
    world_transformation=total_rotation,
)

# * traslo la sfera di -2 metri lungo l'asse y e di 1 metro lungo l'asse z (segni rispetto alla camera)
bpy.data.objects["sphere"].location = (0, 4, -6)

blensor.blendodyne.scan_advanced(
    current_sensor,
    rotation_speed=10.0,
    simulation_fps=24,
    angle_resolution=0.1728,
    max_distance=300,
    evd_file="scan_sphere_trasl.numpy",
    noise_mu=0.0,
    noise_sigma=0.03,
    start_angle=0,
    end_angle=360,
    evd_last_scan=True,
    add_blender_mesh=False,
    add_noisy_blender_mesh=False,
    world_transformation=total_rotation,
)

scan = np.loadtxt("scan_sphere00000.numpy")
df = pd.DataFrame(scan, columns=data["columns"])
df.to_csv("scan_sphere.csv", index=False)

scan_trasl = np.loadtxt("scan_sphere_trasl00000.numpy")
df_trasl = pd.DataFrame(scan_trasl, columns=data["columns"])
df_trasl.to_csv("scan_sphere_trasl.csv", index=False)
