"""
Module de modèles proxy qui charge les modèles appropriés selon le mode
"""

import os

# Déterminer le mode à partir de la variable d'environnement
# Ceci est évalué au moment du chargement du module
STANDALONE_MODE = os.environ.get('FLASK_ENV') == 'standalone'

if STANDALONE_MODE:
    # Mode standalone : utiliser les modèles simplifiés
    from app.models_standalone import *
else:
    # Mode serveur : utiliser les modèles complets
    from app.models_server import *
