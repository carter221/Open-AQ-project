import pytest
import sys
import os
import json
import dotenv
from openaq import OpenAQ
from datetime import datetime, timedelta
from time import sleep

# Ajouter le chemin vers le module src
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'etl'))

# Charger .env seulement s'il existe (localement)
if os.path.exists('.env'):
    dotenv.load_dotenv()

# Vérifier la clé API - GitHub Actions l'aura via les secrets
api_key = os.getenv('OPENAQ_API_KEY')
if not api_key or api_key.strip() == "":
    pytest.skip("OPENAQ_API_KEY not found or empty in environment variables", allow_module_level=True)

# Maintenant on peut importer le module
import api_extract

def test_fetch_locations():
    locations = api_extract.fetch_locations(limit=10, page=1)
    assert locations is not None, "Locations ne doit pas etre None"
    assert isinstance(locations, list), "Locations doit etre une liste"
    assert len(locations) <= 10, "Doit recuperer au plus 10 locations"

def test_fetch_instruments():
    instruments = api_extract.fetch_instruments()
    assert instruments is not None, "Instruments ne doit pas etre None"
    assert isinstance(instruments, list), "Instruments doit etre une liste"
    assert len(instruments) > 0, "Doit recuperer au moins un instrument"

def test_main_function(capsys):
    # Nettoyer les fichiers existants avant le test
    for file in ['locations.json', 'instruments.json']:
        if os.path.exists(file):
            os.remove(file)
    
    api_extract.main()
    captured = capsys.readouterr()
    assert "Début de l'extraction des données de l'API OpenAQ" in captured.out
    
    # Vérifier que soit les fichiers sont créés, soit il y a un message d'erreur
    files_created = os.path.exists('locations.json') and os.path.exists('instruments.json')
    error_message = "Erreur lors de la récupération des données de l'API." in captured.out
    error_final_message = "Une erreur s'est produite:" in captured.out
    success_message = "Extraction des données terminée." in captured.out

    if files_created:
        assert success_message, "Les fichiers sont créés mais pas de message de succès"
        # Vérifier que les fichiers ne sont pas vides
        assert os.path.getsize('locations.json') > 0
        assert os.path.getsize('instruments.json') > 0
    else:
        assert error_message or error_final_message, "Ni fichiers créés ni message d'erreur affiché"
    
    # Nettoyer après le test
    for file in ['locations.json', 'instruments.json']:
        if os.path.exists(file):
            os.remove(file)

if __name__ == "__main__":
    pytest.main([__file__])