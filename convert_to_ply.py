from pyntcloud import PyntCloud
from mathutils import *
from math import *
import pandas as pd
import os
import re

# * parsing argomenti e documentazione
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


def extract_sort_key(nome_file):
    # Usa un'espressione regolare per estrarre tutti i numeri dal nome del file
    numeri = re.findall(r"\d+", nome_file)
    # Converte i numeri estratti in interi
    return [int(numero) for numero in numeri]


# Ottieni la lista dei file nella cartella
lista_file = sorted(os.listdir(origin), key=extract_sort_key)

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
    percorso_completo = os.path.basename(percorso_completo).split(".")[0]
    destination = destination.replace("\\", "/")
    cloud = PyntCloud(df)
    cloud.to_file(f"{destination}/{percorso_completo}.ply")
