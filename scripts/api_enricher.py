# scripts/api_enricher.py - VERSIÓN MEJORADA
import pandas as pd
import requests
import time
import json
import os
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

print("🌍 API ENRICHER - Mejorado para Lima")
print("="*50)

def safe_geocode(location, geolocator, retries=3):
    """Geocodificación segura con reintentos"""
    if not location or pd.isna(location):
        return None
    
    for attempt in range(retries):
        try:
            # Primero intentar con el nombre completo
            result = geolocator.geocode(location, timeout=10)
            if result:
                return result
            
            # Si falla, extraer solo el distrito
            parts = location.split(',')
            if len(parts) > 1:
                district = parts[1].strip() + ", Lima, Perú"
                result = geolocator.geocode(district, timeout=10)
                if result:
                    return result
            
            # Último intento: solo "Lima, Perú"
            result = geolocator.geocode("Lima, Perú", timeout=10)
            return result
            
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            if attempt < retries - 1:
                time.sleep(1)
                continue
            print(f"⚠️  Error geocoding {location}: {e}")
            return None
    
    return None

def main():
    # Cargar propiedades procesadas
    input_path = "data/processed/scored_properties.csv"
    
    if not os.path.exists(input_path):
        print(f"❌ No se encontró: {input_path}")
        print("💡 Ejecuta primero: python scripts/data_processor.py")
        return
    
    df = pd.read_csv(input_path)
    print(f"📊 {len(df)} propiedades cargadas")
    
    # Inicializar geocodificador
    geolocator = Nominatim(user_agent="lima_housing_analytics")
    
    # Columnas para coordenadas
    df['latitude'] = None
    df['longitude'] = None
    df['osm_data'] = None
    
    # Contadores
    found = 0
    not_found = 0
    
    print("\n📍 Buscando coordenadas...")
    print("-"*40)
    
    # Procesar cada propiedad
    for idx, row in df.iterrows():
        location = row.get('location', '')
        
        if pd.isna(location) or not location:
            not_found += 1
            continue
        
        # Intentar geocodificación
        result = safe_geocode(str(location), geolocator)
        
        if result:
            df.at[idx, 'latitude'] = result.latitude
            df.at[idx, 'longitude'] = result.longitude
            df.at[idx, 'osm_data'] = result.address
            found += 1
            
            if found <= 5:  # Mostrar primeros éxitos
                print(f"✅ {location[:40]}... → {result.latitude:.4f}, {result.longitude:.4f}")
        else:
            not_found += 1
            if not_found <= 5:  # Mostrar primeros fallos
                print(f"⚠️  No encontrado: {location[:40]}...")
        
        # Pausa para no saturar la API
        time.sleep(1)
        
        # Mostrar progreso cada 50 propiedades
        if (idx + 1) % 50 == 0:
            print(f"📈 Progreso: {idx + 1}/{len(df)} ({found} encontradas)")
    
    print("\n" + "="*50)
    print("📊 RESULTADOS:")
    print(f"   ✅ Encontradas: {found} propiedades")
    print(f"   ⚠️  No encontradas: {not_found} propiedades")
    print(f"   📍 Tasa de éxito: {(found/len(df)*100):.1f}%")
    
    # Guardar CSV enriquecido
    output_csv = "data/processed/enriched_properties.csv"
    df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"\n💾 CSV guardado: {output_csv}")
    
    # Crear JSON para frontend (solo propiedades con coordenadas)
    properties_with_coords = df[df['latitude'].notna()].to_dict('records')
    
    output_json = "web/data/properties.json"
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(properties_with_coords, f, indent=2, ensure_ascii=False)
    
    print(f"📄 JSON guardado: {output_json}")
    print(f"   (con {len(properties_with_coords)} propiedades con coordenadas)")
    
    # Mostrar estadísticas por distrito
    print("\n🏙️  ESTADÍSTICAS POR DISTRITO:")
    print("-"*40)
    
    df['has_coords'] = df['latitude'].notna()
    stats = df.groupby('district').agg(
        total=('district', 'size'),
        with_coords=('has_coords', 'sum'),
        avg_score=('final_score', 'mean')
    ).round(2)
    
    stats['success_rate'] = (stats['with_coords'] / stats['total'] * 100).round(1)
    print(stats.sort_values('success_rate', ascending=False).head(10))
    
    print("\n✅ ENRIQUECIMIENTO COMPLETADO")

if __name__ == "__main__":
    main()