#!/bin/bash
################################################################################
# Script de lancement KB Support Basedoc - Mode Standalone
################################################################################

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "============================================================"
echo "  KB Support Basedoc - Lancement"
echo "============================================================"
echo ""

# Se placer dans le répertoire du script
cd "$(dirname "$0")"

# Vérifier que Python est installé
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[ERREUR]${NC} Python 3 n'est pas installé"
    echo ""
    echo "Installez Python 3 avec :"
    echo "  sudo apt install python3 python3-venv python3-pip"
    echo ""
    exit 1
fi

# Vérifier que l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}[INFO]${NC} Création de l'environnement virtuel..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERREUR]${NC} Impossible de créer l'environnement virtuel"
        exit 1
    fi
    echo -e "${GREEN}[OK]${NC} Environnement virtuel créé"
fi

# Activer l'environnement virtuel
echo -e "${YELLOW}[INFO]${NC} Activation de l'environnement virtuel..."
source venv/bin/activate

# Vérifier que les dépendances sont installées
python -c "import flask" &> /dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[INFO]${NC} Installation des dépendances..."
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERREUR]${NC} Impossible d'installer les dépendances"
        exit 1
    fi
    echo -e "${GREEN}[OK]${NC} Dépendances installées"
fi

# Vérifier que la base de données existe
if [ ! -f "data/kb_basedoc.db" ]; then
    echo -e "${YELLOW}[INFO]${NC} Initialisation de la base de données..."
    python standalone.py init-db
    if [ $? -ne 0 ]; then
        echo -e "${RED}[ERREUR]${NC} Impossible d'initialiser la base de données"
        exit 1
    fi
    echo -e "${GREEN}[OK]${NC} Base de données initialisée"
fi

# Lancer l'application
echo ""
echo -e "${YELLOW}[INFO]${NC} Lancement de l'application..."
echo ""
python standalone.py

# Si l'application s'arrête
echo ""
echo -e "${YELLOW}[INFO]${NC} Application arrêtée"
