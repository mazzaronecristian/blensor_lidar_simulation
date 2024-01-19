import json
from mathutils import *
import math
from math import *
import numpy as np
import pandas as pd
import os
from pyntcloud import PyntCloud
import re

import argparse

parser = argparse.ArgumentParser(
    description="Converte le un file .csv in un file .ply, utilizzabile per il rendering delle nuvola di punti."
)
# Aggiungi gli argomenti che il tuo script può accettare
parser.add_argument(
    "cartella_origine", type=str, help="Cartella da cui prendere i file .csv"
)
parser.add_argument(
    "cartella_destinazione", type=str, help="cartella in cui salvare i file .ply"
)

# Ottieni gli argomenti dalla riga di comando
args = parser.parse_args()

# Accedi agli argomenti
origin = args.cartella_origine
destination = args.cartella_destinazione

if not os.path.isdir(destination):
    os.makedirs(destination)
# Fai qualcosa con gli argomenti
print(f"Argomento 1: {origin}")
print(f"Argomento 2: {destination}")


def estrai_numeri_da_nome_file(nome_file):
    # Usa un'espressione regolare per estrarre tutti i numeri dal nome del file
    numeri = re.findall(r"\d+", nome_file)
    # Converte i numeri estratti in interi
    return [int(numero) for numero in numeri]


# Ottieni la lista dei file nella cartella
lista_file = sorted(os.listdir(origin), key=estrai_numeri_da_nome_file)

# Esegui un ciclo for per iterare sui file
for i, nome_file in enumerate(lista_file):
    # Crea il percorso completo al file
    percorso_completo = os.path.join(origin, nome_file)
    print(f"converting: {percorso_completo}")
    percorso_completo = percorso_completo.replace("\\", "/")
    df = pd.read_csv(percorso_completo)
    if df.empty:
        continue

    # *taglia la stringa percorso_completo dal primo / in poi
    percorso_completo = os.path.basename(percorso_completo)
    destination = destination.replace("\\", "/")
    cloud = PyntCloud(df)
    cloud.to_file(f"{destination}/{percorso_completo}.ply")

# # * pulisce la scena
# bpy.ops.object.select_all(action="SELECT")
# bpy.ops.object.delete()

# # * aggiungo un punto luce
# bpy.ops.object.lamp_add(type="POINT", location=(0, 4, 5))

# # # * carico la camera di riferimento per il rendering
# bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(math.radians(80), 0, 0))
# render_camera = bpy.context.object
# render_camera.name = "camera"
# render_camera.data.name = f"{render_camera.name}_Data"
# bpy.context.scene.camera = render_camera

# # * carico la nuvola di punti come .ply (Stanford Polygon Library)
# bpy.ops.import_mesh.ply(filepath="output.ply")
# point_cloud = bpy.context.selected_objects[0]
# point_cloud.location = (0, 0, 0)
# point_cloud.rotation_euler = (0, 0, 0)
# point_cloud.name = "point_cloud"

# bpy.ops.object.editmode_toggle()
# bpy.ops.mesh.extrude_region_move()
# mat = bpy.data.materials.new(name="Material")
# mat.type = "WIRE"
# mat.emit = 10
# point_cloud.data.materials.append(mat)

# bpy.ops.object.editmode_toggle()

# path = "//rendering/rendered.png"
# bpy.context.scene.render.filepath = path
# bpy.context.scene.render.image_settings.file_format = "PNG"
# bpy.ops.render.render(use_viewport=True, write_still=True)

# bpy.ops.object.select_all(action="SELECT")
# bpy.ops.object.delete()

# # Lista dei percorsi dei file da importare per ogni keyframe
# percorsi_import = [
#     "output.ply",
#     "point_cloud.ply"
#     # Aggiungi altri percorsi secondo necessità
# ]

# # Impostazioni comuni per l'importazione
# import_settings = {
#     "location": (0, 0, 0),
#     "rotation": (0, 0, 0),
# }

# # * carica tutti i mesh presenti in percorsi_import con le impostazioni di import_settings
# for i, path in enumerate(percorsi_import):
#     bpy.ops.import_mesh.ply(filepath=path)
#     mesh = bpy.context.selected_objects[0]
#     mesh.location = import_settings["location"]
#     mesh.rotation_euler = import_settings["rotation"]
#     mesh.name = f"mesh_{i}"

    # bpy.ops.object.editmode_toggle()
    # bpy.ops.mesh.extrude_region_move(
    #     MESH_OT_extrude_region={"mirror": False},
    #     TRANSFORM_OT_translate={
    #         "value": (0, -0, 0),
    #     },
    # )
    # mat = bpy.data.materials.get("Material")
    # if mat is None:
    #     mat = bpy.data.materials.new(name="Material")
    #     mat.type = "WIRE"
    #     mat.emit = 10
    # mesh.data.materials.append(mat)
# bpy.ops.mesh.extrude_region_move(
#     MESH_OT_extrude_region={"mirror": False},
#     TRANSFORM_OT_translate={
#         "value": (-0, 0, 0),
#         "constraint_axis": (False, False, False),
#         "constraint_orientation": "GLOBAL",
#         "mirror": False,
#         "proportional": "DISABLED",
#         "proportional_edit_falloff": "SMOOTH",
#         "proportional_size": 1,
#         "snap": False,
#         "snap_target": "CLOSEST",
#         "snap_point": (0, 0, 0),
#         "snap_align": False,
#         "snap_normal": (0, 0, 0),
#         "gpencil_strokes": False,
#         "texture_space": False,
#         "remove_on_cancel": False,
#         "release_confirm": False,
#         "use_accurate": False,
#     },
# )
