## Come installare il modulo scneario nel proprio ambiente virtuale

È consigliabile installare il modulo scenario nel proprio ambiente virtuale, così da non dover tenere due copie della cartella scenario (una nella cartella del progetto e una negli addons di Blender). Ecco come fare:

- Spostare la cartella scenario nella cartella degli addonso di Blender;
- Aprire il terminale di conda (Anaconda prompt) in modalità amministratore;
- navigare nella cartella scenario contenuta nella cartella degli addons di Blender;
- attivare l'ambiente virtuale in cui si vuole installare il modulo scenario (conda activate nome_ambiente);
- eseguire il comando python setup.py install (o python setup.py develop, per installare il modulo in modalità sviluppo);
