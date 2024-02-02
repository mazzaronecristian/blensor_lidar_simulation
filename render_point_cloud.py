import sys
import render_ply as rp

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

rp.render_point_clouds(origin, destination)