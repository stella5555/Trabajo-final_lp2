# scripts/create_full_json.py
import pandas as pd
import json
import os

print("📊 CREANDO JSON COMPLETO A PARTIR DEL CSV...")

# Cargar el CSV procesado
csv_path = "data/processed/scored_properties.csv"
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    print(f"✅ CSV cargado: {len(df)} propiedades")
    
    # Convertir a diccionario
    properties = df.to_dict('records')
    
    # Guardar como JSON
    output_path = "web/data/properties.json"
    
    # Asegurar que la carpeta existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(properties, f, indent=2, ensure_ascii=False)
    
    print(f"✅ JSON generado: {output_path}")
    print(f"📊 Total propiedades en JSON: {len(properties)}")
    
    # Mostrar estadísticas
    print("\n📈 ESTADÍSTICAS:")
    print(f"  Precio promedio: S/. {df['price_clean'].mean():.0f}")
    print(f"  Área promedio: {df['area_clean'].mean():.0f} m²")
    print(f"  Score máximo: {df['final_score'].max():.1f}")
    print(f"  Score mínimo: {df['final_score'].min():.1f}")
    print(f"  Score promedio: {df['final_score'].mean():.1f}")
    
else:
    print(f"❌ No se encontró el archivo: {csv_path}")
    print("Ejecuta primero: python scripts/data_processor.py")