
import bpy
import math
import os
import re
import pandas as pd

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

def obtain_cloud_list(origin):
    # * Ottieni la lista dei file nella cartella ordinati nel modo giusto
    lista_file = sorted(os.listdir(origin), key=extract_sort_key)

    # * salvo in point_clouds i percorsi completi ai file .ply da renderizzare
    point_clouds = []
    for file in lista_file:
        complete_path = os.path.join(origin, file)
        if file.endswith(".ply"):
            point_clouds.append(complete_path)
    return point_clouds

def render_point_clouds(origin, destination):
    point_clouds = obtain_cloud_list(origin)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    # * aggiungo un punto luce
    bpy.ops.object.lamp_add(type="POINT", location=(0, 4, 5))
    bpy.context.object.name = 'Lamp'
    lamp_name = bpy.context.object.name

    #* genero il materiale di tipo wire da assegnare alla nuvola di punti
    mat = bpy.data.materials.new(name="Material")
    mat.type = "WIRE"
    mat.emit = 10
    substrings = os.path.basename(point_clouds[0]).split(".")[0].split("_")
    
    latest_sensor = None

    camera_details = pd.read_csv("camera_details.csv")
    camera_details = camera_details.groupby("target_sensor")

    # * carico la nuvola di punti come .ply (Stanford Polygon Library)
    for i, path in enumerate(point_clouds):
        #* Carico la nuvola 
        bpy.ops.import_mesh.ply(filepath=path)
        #*edita la nuvola di punti e vi assegna il materiale wire
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.extrude_region_move()
        bpy.context.object.data.materials.append(mat)
        bpy.ops.object.editmode_toggle()
        point_cloud_name = bpy.context.object.name
        substrings = point_cloud_name.split("_")

        #* ottengo current_sensor
        current_sensor = substrings[0]+"_"+substrings[1]
        if latest_sensor == None:
            render_cameras = load_cameras(current_sensor, camera_details)

        if latest_sensor != None and current_sensor != latest_sensor:
            #*pulisco la scena dagli oggetti usati per la precedente iterazione mantenendo la luce
            bpy.ops.object.select_all(action="SELECT")
            bpy.data.objects[lamp_name].select = False
            bpy.data.objects[bpy.context.object.name].select = False
            bpy.ops.object.delete()
            render_cameras = load_cameras(current_sensor, camera_details)

        #* Rendering
        for render_camera in render_cameras:
            bpy.context.scene.camera = render_camera
            path = f"//{destination}/{current_sensor}/{bpy.context.scene.camera.name}_{substrings[2]}.png"
            bpy.context.scene.render.filepath = path
            bpy.context.scene.render.image_settings.file_format = "PNG"
            bpy.ops.render.render(use_viewport=True, write_still=True)
        
        latest_sensor = current_sensor

        #*rimuovo la nuvola di punti precedente 
        bpy.ops.object.select_all(action="DESELECT")
        bpy.data.objects[point_cloud_name].select = True
        bpy.ops.object.delete()