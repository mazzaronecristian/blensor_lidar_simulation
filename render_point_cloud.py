import bpy
import math
import os
import re
import pandas as pd
# TODO: esegui rendering delle nuvole di punti date in input
import sys

args = sys.argv
args = args[args.index("--") + 1 :]  # get all args after "--"

if len(args) < 2 and args[-1] != "h":
    print("Numero di argomenti non valido")
    exit(1)
if args[-1] == "h":
    print("blender [-b] -P render_point_cloud.py -- <ply_file_directory> <destination>")
    print(
        "Esegue il rendering delle nuvole di punti presenti nella cartella <ply_file_directory> e salva le immagini nella cartella <destination> in formato PNG"
    )
    print(
        "--:                  Blender ignora tutti gli argomenti dopo => inserire gli argomenti dello script PYTHON dopo --"
    )
    print("ply_file_directory:  cartella contenente i file .ply")
    print("destination:         cartella in cui salvare le immagini in formato PNG")
    print("-b:                  esegue lo script in background")
    print("-P or --python:      esegue lo script Python")
    exit(0)

origin = args[-2].replace("\\", "/")
destination = args[-1].replace("\\", "/")


def extract_sort_key(nome_file):
    # Usa un'espressione regolare per estrarre tutti i numeri dal nome del file
    numeri = re.findall(r"\d+", nome_file)
    # Converte i numeri estratti in interi
    return [int(numero) for numero in numeri]

def load_cameras(sensor_name, camera_details):
    cameras = camera_details.get_group(sensor_name)
    render_cameras = []
    for i, camera in cameras.iterrows():
        bpy.ops.object.camera_add(location=(camera["x"],camera["y"],camera["z"]), 
                                rotation=(math.radians(camera["x_rotation"]), math.radians(camera["y_rotation"]), math.radians(camera["z_rotation"])))
        render_camera = bpy.context.object
        render_camera.name = camera["name"]
        render_camera.data.name = f"{render_camera.name}_Data"
        render_camera.data.lens = camera["lens"]
        render_cameras.append(render_camera)
    return render_cameras

# * Ottieni la lista dei file nella cartella ordinati nel modo giusto
lista_file = sorted(os.listdir(origin), key=extract_sort_key)

# * salvo in point_clouds i percorsi completi ai file .ply da renderizzare
point_clouds = []
for file in lista_file:
    complete_path = os.path.join(origin, file)
    if file.endswith(".ply"):
        point_clouds.append(complete_path)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()
# * aggiungo un punto luce
bpy.ops.object.lamp_add(type="POINT", location=(0, 4, 5))

# * carico la camera di riferimento per il rendering
# bpy.ops.object.camera_add(location=(0, 0, 2), 
#                           rotation=(math.radians(90), 0, math.radians(220)))
# render_camera = bpy.context.object
# render_camera.name = "camera"
# render_camera.data.name = f"{render_camera.name}_Data"
# render_camera.data.lens = 15
# bpy.context.scene.camera = render_camera

#* genero il materiale di tipo wire da assegnare alla nuvola di punti
mat = bpy.data.materials.new(name="Material")
mat.type = "WIRE"
mat.emit = 10
substrings = os.path.basename(point_clouds[0]).split(".")[0].split("_")
 
latest_sensor = None

camera_details = pd.read_csv("camera_details.csv")
camera_details = camera_details.groupby("target_sensor")


# * carico la nuvola di punti come .ply (Stanford Polygon Library)
for i, path in enumerate(point_clouds[0:5]):
    #* Carico la nuvola e ottengo current_sensor
    bpy.ops.import_mesh.ply(filepath="scans/ply/real_trajs/sensor_2_4.ply")
    #*edita la nuvola di punti e vi assegna il materiale wire
    break
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.extrude_region_move()
    bpy.context.object.data.materials.append(mat)
    bpy.ops.object.editmode_toggle()
    point_cloud_name = bpy.context.object.name
    substrings = point_cloud_name.split("_")
    current_sensor = substrings[0]+"_"+substrings[1]
    if latest_sensor == None:
        render_cameras = load_cameras(current_sensor, camera_details)

    if latest_sensor != None and current_sensor != latest_sensor:
        #*pulisco la scena dagli oggetti usati per la precedente iterazione mantenendo la luce
        bpy.ops.object.select_all(action="SELECT")
        bpy.data.objects['Lamp'].select = False
        bpy.data.objects[bpy.context.object.name].select = False
        bpy.ops.object.delete()
        render_cameras = load_cameras(current_sensor, camera_details)

    #* Rendering
    for render_camera in render_cameras:
        bpy.context.scene.camera = render_camera
        path = f"//image_render/{current_sensor}/{bpy.context.scene.camera.name}_{substrings[2]}.png"
        bpy.context.scene.render.filepath = path
        bpy.context.scene.render.image_settings.file_format = "PNG"
        bpy.ops.render.render(use_viewport=True, write_still=True)
    
    latest_sensor = current_sensor

    #*rimuovo la nuvola di punti precedente 
    bpy.ops.object.select_all(action="DESELECT")
    bpy.data.objects[point_cloud_name].select = True
    bpy.ops.object.delete()
# exit()

# ? vecchio codice, prendere spunto per il nuovo
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
