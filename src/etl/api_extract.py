import requests
import json
import os
import dotenv
from openaq import OpenAQ
from datetime import datetime, timedelta
from time import sleep

dotenv.load_dotenv()

api_key = os.getenv('OPENAQ_API_KEY')
if not api_key:
    raise Exception("OPENAQ_API_KEY not found in environment variables")

client = OpenAQ(api_key=api_key)

if not client:
    raise Exception("Failed to initialize OpenAQ client. Check your API key.")

def fetch_locations(limit=300, page=2):
    try:
        response = client.locations.list(limit=limit, page=page)
        return response.results if hasattr(response, 'results') else response
    except Exception as e:
        print(f"Error fetching locations: {e}")
        return []

def fetch_instruments():
    try:
        response = client.instruments.list()
        return response.results if hasattr(response, 'results') else response
    except Exception as e:
        print(f"Error fetching instruments: {e}")
        return []

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
            # Convertir les objets en dictionnaires
            locations_data = []
            for location in locations:
                if hasattr(location, '__dict__'):
                    locations_data.append(location.__dict__)
                elif hasattr(location, 'to_dict'):
                    locations_data.append(location.to_dict())
                else:
                    locations_data.append(str(location))
            
            instruments_data = []
            for instrument in instruments:
                if hasattr(instrument, '__dict__'):
                    instruments_data.append(instrument.__dict__)
                elif hasattr(instrument, 'to_dict'):
                    instruments_data.append(instrument.to_dict())
                else:
                    instruments_data.append(str(instrument))
            
            with open('locations.json', 'w') as loc_file:
                json.dump(locations_data, loc_file, indent=4, default=str)

            with open('instruments.json', 'w') as inst_file:
                json.dump(instruments_data, inst_file, indent=4, default=str)

            print("Extraction des données terminée. Fichiers enregistrés : locations.json, instruments.json")
    except Exception as e:
        print(f"Une erreur s'est produite: {e}")
    finally:
        sleep(1)
        client.close()

if __name__ == "__main__":
    main()