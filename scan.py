import bpy
import math
from bpy import data as D
from bpy import context as C
from mathutils import *
from math import *
import blensor
import numpy as np
import pandas as pd
import json

#* eseguire il comando "blender -P scan.py" per aprire blender e eseguire lo script
#* eseguire il comando "blender -b -P scan.py" per eseguire lo script in background

#* Elimina tutti gli oggetti nella scena
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Modello Ford Thunderbird 1961
car_model =  "assets/car.obj"
#* definisce una classe per le coordinate, intese come posiione e rotazione dell'oggetto nel blender
class Coordinates:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

#* definisce posizioni e rotazioni della macchina e della camera

loc_rot = pd.read_csv("keyframes.csv")

# Carica il modello della macchina nella scena
bpy.ops.import_scene.obj(filepath=car_model)


# Posiziona la macchina nella scena (esempio: posizioniamola a X=0, Y=0, Z=0)
car_object = bpy.context.selected_objects[0]  # Seleziona il primo oggetto importato (la macchina)
car_object.location = (loc_rot["car_position"][0], loc_rot["car_position"][1], loc_rot["car_position"][2])  # Imposta la posizione desiderata 
car_object.rotation_euler = ( math.radians( loc_rot["car_rotation"][0] ), math.radians( loc_rot["car_rotation"][1] ), math.radians( loc_rot["car_rotation"][2] ) )

#* Crea un cubo, un ostacolo per le prove dei sensori
# bpy.ops.mesh.primitive_cube_add(radius = 1.0, location = (0,0,1.3), rotation = (0,0,0))

# Aggiungi le 4 camere nella scena
for i in range(4):
    bpy.ops.object.camera_add(
        location=(
            loc_rot[f"camera_{i}_position"][0],
            loc_rot[f"camera_{i}_position"][1], 
            loc_rot[f"camera_{i}_position"][2] 
        ),
        rotation=(
            math.radians( loc_rot[f"camera_{i}_rotation"][0] ), 
            math.radians( loc_rot[f"camera_{i}_rotation"][1] ),
            math.radians( loc_rot[f"camera_{i}_rotation"][2] )
        )
    )  # Imposta la posizione della camera
    camera_corrente = bpy.context.object
    #* rinomina la camera e i dati della camera
    camera_corrente.name = f"camera_{i}"  
    camera_corrente.data.name = f"Camera_{i}_Data"


#* Crea un piano (superficie piana), assimilabile alla strada
bpy.ops.mesh.primitive_plane_add(radius=10.0, location=(0,0,0.3), rotation=(0,0,0))
plane = bpy.data.objects["Plane"]

#* Crea un cubo, un ostacolo per le prove dei sensori
# bpy.ops.mesh.primitive_cube_add(radius = 1.0, location = (-1.0, 10.0, 1.3), rotation = (0,0,0))

#* prende le colonne dal file data.json
with open('data.json', 'r') as file:
    data = json.load(file)

#* eseguo una scansione con ogni camera. Una per volta
for i in range(4):
    #* attivo la camera "camera_i"
    camera = bpy.data.objects[f"camera_{i}"]
    bpy.context.scene.camera = camera

    
    rotation_scan_x = Matrix.Rotation(camera.rotation_euler[0], 4, 'X')
    rotation_scan_y = Matrix.Rotation(camera.rotation_euler[1], 4, 'Y')
    rotation_scan_z = Matrix.Rotation(camera.rotation_euler[2], 4, 'Z')


    # ottiei total_rotation in un altro modo (non funziona)
    # non usare l'operatore @, ma il metodo .multiply()
    total_rotation = rotation_scan_z * rotation_scan_y * rotation_scan_x


    #* I punti della scansione vengono calolati in modo assoluto rispetto alla scena
    #* local_coordinates = False allora i punti della scansione vengono calcolati in modo assoluto
    # local_coordinates = True allora i punti della scansione vengono calcolati in modo relativo alla camera
    blensor.blendodyne.scan_advanced(camera, rotation_speed = 10.0, 
                                   simulation_fps=24, angle_resolution = 0.1728, 
                                   max_distance = 100, evd_file= f"scan_camera_{i}.numpy",
                                   noise_mu=0.0, noise_sigma=0.03, start_angle = -90.0, 
                                   end_angle = 90.0, evd_last_scan=True, 
                                   add_blender_mesh = False, 
                                   add_noisy_blender_mesh = False,
                                   world_transformation=total_rotation)

    scan = np.loadtxt(f"scan_camera_{i}00000.numpy")
    rounded_scan = np.round(scan, decimals=3)

    #* filtro i punti dello scan on z = 0.3 (pavimento), per eliminare i punti che intersecano la strada
    filtered = rounded_scan[rounded_scan[:,7] != -3.2]

    #* crea un dataframe pandas con tutti i punti filtrati
    df = pd.DataFrame(filtered, columns=data['columns'])
    df.to_csv(f"scan_camera_{i}.csv", index=False)

#* la distanza è calcolata con: coordinata ostacolo - coordinata camera
#* le distanze sono ricavate con la formula: coordinata camera - coordinata ostcolo senza fare il modulo