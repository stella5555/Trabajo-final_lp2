# scripts/api_enricher.py
import pandas as pd
import requests
import time
import os

def enrich_with_osm(csv_path='data/processed/scored_properties.csv', sample_size=15):
    """
    Toma el CSV con scores y agrega coordenadas usando API OpenStreetMap.
    Solo procesa 'sample_size' propiedades para no saturar la API.
    """
    print("🌍 CONECTANDO CON API OPENSTREETMAP...")
    
    # Cargar los datos ya procesados
    df = pd.read_csv(csv_path, encoding='utf-8')
    print(f"   📊 {len(df)} propiedades cargadas")
    
    # Inicializar columnas para coordenadas
    df['latitude'] = None
    df['longitude'] = None
    df['osm_data'] = None
    
    # Contador para límite de API
    processed = 0
    
    for idx, row in df.head(sample_size).iterrows():
        try:
            # Extraer la dirección básica (primer elemento antes de la primera coma)
            location_parts = str(row['location']).split(',')
            if len(location_parts) > 0:
                query_location = location_parts[0].strip()
                
                # Construir consulta para API
                url = "https://nominatim.openstreetmap.org/search"
                params = {
                    'q': f"{query_location}, Lima, Peru",
                    'format': 'json',
                    'limit': 1,
                    'countrycodes': 'PE'  # Solo Perú
                }
                headers = {
                    'User-Agent': 'Lima-Housing-Analytics-Project/1.0 (https://github.com/tu-usuario/tu-repo)'
                }
                
                # Hacer la petición a la API
                response = requests.get(url, params=params, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        # Guardar coordenadas y datos adicionales
                        df.at[idx, 'latitude'] = float(data[0]['lat'])
                        df.at[idx, 'longitude'] = float(data[0]['lon'])
                        df.at[idx, 'osm_data'] = str(data[0].get('display_name', ''))
                        
                        print(f"   ✅ {query_location}: {data[0]['lat']}, {data[0]['lon']}")
                        processed += 1
                    else:
                        print(f"   ⚠️  {query_location}: No encontrado en OSM")
                else:
                    print(f"   ❌ Error API: código {response.status_code}")
            
            # Pausa para ser respetuoso con la API (1 solicitud por segundo)
            time.sleep(1.2)
            
            # Detener si alcanzamos el límite
            if processed >= sample_size:
                break
                
        except Exception as e:
            print(f"   ❌ Error con {row.get('location', 'desconocido')}: {str(e)}")
            continue
    
    # Guardar resultados enriquecidos
    output_path = 'data/processed/enriched_properties.csv'
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ ENRIQUECIMIENTO COMPLETADO")
    print(f"   📍 {processed} propiedades con coordenadas")
    print(f"   💾 Guardado en: {output_path}")
    
    # También guardar como JSON para el frontend
    json_path = 'web/data/properties.json'
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    
    # Convertir a JSON (solo las propiedades con coordenadas)
    df_with_coords = df.dropna(subset=['latitude', 'longitude'])
    if not df_with_coords.empty:
        df_with_coords.to_json(json_path, orient='records', force_ascii=False)
        print(f"   📄 JSON para frontend: {json_path}")
    
    return df

if __name__ == "__main__":
    # Ejecutar con tamaño de muestra pequeño (15 propiedades)
    enrich_with_osm(sample_size=15)