## Requisiti

- Python 3.6
- conda e conda-forge
- Blender 2.79 con Blensor: Installer sul sito ufficiale di [Blensor](https://www.blensor.org/pages/downloads.html)

## configurazione

Per configurare l'ambiente virtuale di Anaconda con Blender, seguire questo [thread](https://stackoverflow.com/questions/70639689/how-to-use-the-anaconda-environment-on-blender). La versione di python dell'ambiente virtuale deve essere la stessa di quella di Blender (3.6, nel caso di Blender 2.79, con cui funziona Blensor). Così facendo verrà creato un link simbolico tra l'ambiente virtuale e Blender.

### Configurare vs-code per Blender

Per utilizzare vs-code con Blender, seguire questo [tutorial](https://www.youtube.com/watch?v=YUytEtaVrrc). Sostanzialmente è necessario installare il modulo python fake-bpy-module-2.79 (`pip install fake-bpy-module-2.79`) e l'estensione Blender Development di Jacques Lucke, per l'autocompletamento.

### Configurzione di "scenario"

Nella cartella scenario, è presente un README che spiega come isntallare scenario nel proprio ambiente virtuale.
