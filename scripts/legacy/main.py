import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from scripts.legacy.scraper_urbania import main as scrape_urbania
from scripts.api_google import GoogleMapsAPI
from scripts.data_processor import DataProcessor

def main():
    print("="*60)
    print("LIMA HOUSING ANALYTICS - PIPELINE DE DATOS")
    print("="*60)
    
    # 1. Scraping de Urbania
    print("\n1️⃣  EJECUTANDO SCRAPER DE URBANIA...")
    from scripts.legacy.scraper_urbania import main as scrape_main
    scrape_main()
    
    # 2. Procesar datos (esto se completará después)
    print("\n2️⃣  PROCESANDO DATOS...")
    processor = DataProcessor()
    df = processor.load_and_process()
    
    # 3. Enriquecer con Google Maps (se completará después)
    print("\n3️⃣  ENRIQUECIENDO CON GOOGLE MAPS...")
    # google_api = GoogleMapsAPI()
    # df = google_api.enrich_with_places(df)
    
    print("\nPIPELINE COMPLETADO")
    print(f"Datos procesados: {len(df)} registros")
    
    return df

if __name__ == "__main__":
    df = main()

from scripts.api_enricher import main as enrich_data

def main():
    ...
    processor = DataProcessor()
    df = processor.load_and_process()
