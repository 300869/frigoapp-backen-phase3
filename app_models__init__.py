# app/models/__init__.py
# Unifie l'ancien fichier app/models.py (renommé en models_legacy.py)
# avec la nouvelle structure modulaire (alert.py, consumption.py).

# Ré-exporter les modèles Phase 3
from .alert import Alert  # noqa: F401
from .consumption import Consumption  # noqa: F401

# Conserver la compatibilité avec l'ancien fichier monolithique s'il existe
try:
    from .models_legacy import *  # noqa: F401,F403
except Exception:
    pass
