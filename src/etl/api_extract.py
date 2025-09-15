import requests
import json
import os
import dotenv
from openaq import OpenAQ
from datetime import datetime, timedelta
from time import sleep

# Charger .env seulement s'il existe (pas en CI)
if os.path.exists('.env'):
    dotenv.load_dotenv()

api_key = os.getenv('OPENAQ_API_KEY')
client = None

def get_client():
    """Initialise le client OpenAQ si pas déjà fait"""
    global client
    if client is None:
        if not api_key:
            raise Exception("OPENAQ_API_KEY not found in environment variables")
        client = OpenAQ(api_key=api_key)
    return client

def fetch_locations(limit=300, page=2):
    try:
        client = get_client()  # Utiliser get_client() au lieu de client global
        response = client.locations.list(limit=limit, page=page)
        return response.results if hasattr(response, 'results') else response
    except Exception as e:
        print(f"Error fetching locations: {e}")
        return []

def fetch_instruments():
    try:
        client = get_client()  # Utiliser get_client() au lieu de client global
        response = client.instruments.list()
        return response.results if hasattr(response, 'results') else response
    except Exception as e:
        print(f"Error fetching instruments: {e}")
        return []

def convert_to_serializable(obj_list):
    """Convertit une liste d'objets en dictionnaires sérialisables"""
    serializable_data = []
    for obj in obj_list:
        if hasattr(obj, '__dict__'):
            serializable_data.append(obj.__dict__)
        elif hasattr(obj, 'to_dict'):
            serializable_data.append(obj.to_dict())
        else:
            serializable_data.append(str(obj))
    return serializable_data

def main():
    print("Début de l'extraction des données de l'API OpenAQ")

    try:
        locations = fetch_locations()
        instruments = fetch_instruments()

        print(f"Nombre de locations récupérées: {len(locations) if locations else 0}")
        print(f"Nombre d'instruments récupérés: {len(instruments) if instruments else 0}")

        if not locations or not instruments:
            print("Erreur lors de la récupération des données de l'API.")
            return
        else:
            print("Début de l'écriture des fichiers JSON")
            
            # Utiliser la fonction convert_to_serializable
            locations_data = convert_to_serializable(locations)
            instruments_data = convert_to_serializable(instruments)
            
            with open('locations.json', 'w') as loc_file:
                json.dump(locations_data, loc_file, indent=4, default=str)

            with open('instruments.json', 'w') as inst_file:
                json.dump(instruments_data, inst_file, indent=4, default=str)

            print("Extraction des données terminée. Fichiers enregistrés : locations.json, instruments.json")
    except Exception as e:
        print(f"Une erreur s'est produite: {e}")
    finally:
        sleep(1)
        # Vérifier que client existe avant de le fermer
        if client and hasattr(client, 'close'):
            client.close()

if __name__ == "__main__":
    main()