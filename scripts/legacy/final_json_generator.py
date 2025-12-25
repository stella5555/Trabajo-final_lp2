import pandas as pd
import json
import os

print("🔄 COMBINANDO DATOS PROCESADOS + COORDENADAS")
print("="*50)

# 1. Cargar CSV con todos los datos procesados
csv_path = "data/processed/scored_properties.csv"
df_csv = pd.read_csv(csv_path)
print(f"📊 CSV cargado: {len(df_csv)} propiedades con todos los datos")

# 2. Cargar CSV enriquecido con coordenadas
enriched_path = "data/processed/enriched_properties.csv"
if os.path.exists(enriched_path):
    df_enriched = pd.read_csv(enriched_path)
    
    # Combinar manteniendo TODAS las columnas del CSV original
    # y añadiendo solo latitud/longitud del enriquecido
    final_df = df_csv.copy()
    
    # Añadir coordenadas si existen en el enriquecido
    if 'latitude' in df_enriched.columns and 'longitude' in df_enriched.columns:
        final_df['latitude'] = df_enriched['latitude']
        final_df['longitude'] = df_enriched['longitude']
        print(f"📍 Coordenadas añadidas: 100%")
    
    # Guardar JSON FINAL con TODOS los datos
    output_json = "web/data/properties.json"
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    
    properties = final_df.to_dict('records')
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(properties, f, indent=2, ensure_ascii=False)
    
    print(f"✅ JSON FINAL generado: {output_json}")
    print(f"📊 Total propiedades: {len(properties)}")
    print(f"📋 Columnas incluidas: {list(final_df.columns)}")
    
    # Mostrar ejemplo
    print(f"\n📄 EJEMPLO de propiedad:")
    print(json.dumps(properties[0], indent=2)[:500] + "...")
    
else:
    print(f"⚠️  No se encontró {enriched_path}")
    print("💡 Ejecuta primero: python scripts/api_enricher.py")

print("\n🎯 JSON listo para el dashboard!")
