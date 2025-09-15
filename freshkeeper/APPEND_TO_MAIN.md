# Patch pour app/main.py

Dans app/main.py ajoute :

from freshkeeper.jobs.scheduler import start_scheduler

# Dans la fonction create_app() ou après init FastAPI :
start_scheduler()

