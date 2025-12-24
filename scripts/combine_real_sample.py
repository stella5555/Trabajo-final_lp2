# scripts/combine_real_sample.py
import pandas as pd
import os
import numpy as np

def combine_datasets():
    """Combina datos reales de Urbania con datos de muestra"""
    print("🔄 COMBINANDO DATOS REALES + MUESTRA")
    print("="*50)
    
    # 1. Cargar datos REALES (si existen)
    real_data = None
    real_path = "data/raw/urbania_properties.csv"
    
    if os.path.exists(real_path):
        real_df = pd.read_csv(real_path)
        print(f"✅ Datos REALES encontrados: {len(real_df)} propiedades")
        
        # Limpiar y estandarizar datos reales
        real_df['source'] = 'urbania_real'
        real_df['scraped_date'] = pd.Timestamp.now().strftime('%Y-%m-%d')
        
        # Renombrar columnas si es necesario
        column_map = {
            'title': 'title',
            'price': 'price_soles',
            'area': 'area_m2',
            'bedrooms': 'bedrooms',
            'district': 'district',
            'address': 'address'
        }
        
        # Mantener solo columnas que existan
        real_cols = {}
        for new_name, old_name in column_map.items():
            if old_name in real_df.columns:
                real_cols[old_name] = new_name
        
        real_df = real_df.rename(columns=real_cols)
        
        # Añadir columnas faltantes con valores por defecto
        if 'price_soles' not in real_df.columns and 'price' in real_df.columns:
            real_df['price_soles'] = real_df['price']
        
        real_data = real_df
    else:
        print(f"⚠️  No se encontraron datos reales en {real_path}")
    
    # 2. Cargar datos de MUESTRA
    sample_path = "data/processed/dataset_final.csv"
    if os.path.exists(sample_path):
        sample_df = pd.read_csv(sample_path)
        print(f"✅ Datos de MUESTRA: {len(sample_df)} propiedades")
        
        # Marcar como muestra
        sample_df['source'] = 'sample_data'
    else:
        print("❌ No hay datos de muestra. Ejecuta primero: python scripts/create_sample_data.py")
        return
    
    # 3. COMBINAR (si hay datos reales)
    if real_data is not None and len(real_data) > 0:
        # Combinar manteniendo todas las columnas
        combined_df = pd.concat([real_data, sample_df], ignore_index=True, sort=False)
        print(f"📊 TOTAL COMBINADO: {len(combined_df)} propiedades")
        print(f"   - Reales: {len(real_data)} de Urbania")
        print(f"   - Muestra: {len(sample_df)} sintéticas")
    else:
        combined_df = sample_df
        print(f"📊 Usando solo datos de muestra: {len(combined_df)} propiedades")
    
    # 4. Calcular SCORES para todas las propiedades
    print("\n📈 CALCULANDO SCORES PARA TODAS LAS PROPIEDADES...")
    
    # Para propiedades reales (sin scores), calcularlos
    mask_real = combined_df['source'] == 'urbania_real'
    
    # Precio por m²
    combined_df['price_per_m2'] = combined_df['price_soles'] / combined_df['area_m2']
    
    # Score de costo (inverso: menor precio = mayor score)
    combined_df['cost_score'] = 10 - (combined_df['price_per_m2'] / 100)
    combined_df['cost_score'] = combined_df['cost_score'].clip(0, 10)
    
    # Para propiedades reales, generar scores de seguridad y servicios realistas
    if mask_real.any():
        # Basado en el distrito (Miraflores tiene buena seguridad)
        district_scores = {
            'miraflores': {'safety': 8.5, 'services': 9.0},
            'surco': {'safety': 8.0, 'services': 8.5},
            'san-isidro': {'safety': 9.0, 'services': 9.5},
            'barranco': {'safety': 7.5, 'services': 8.0},
            'la-molina': {'safety': 8.8, 'services': 8.0}
        }
        
        for idx, row in combined_df[mask_real].iterrows():
            district = str(row['district']).lower().replace(' ', '-').replace('_', '-')
            if district in district_scores:
                combined_df.at[idx, 'safety_score'] = district_scores[district]['safety'] + np.random.uniform(-0.3, 0.3)
                combined_df.at[idx, 'services_score'] = district_scores[district]['services'] + np.random.uniform(-0.3, 0.3)
            else:
                combined_df.at[idx, 'safety_score'] = 7.0 + np.random.uniform(-0.5, 0.5)
                combined_df.at[idx, 'services_score'] = 7.0 + np.random.uniform(-0.5, 0.5)
    
    # Fórmula final de scoring (40/40/20)
    combined_df['final_score'] = (
        combined_df['cost_score'] * 0.4 + 
        combined_df['safety_score'] * 0.4 + 
        combined_df['services_score'] * 0.2
    )
    combined_df['final_score'] = combined_df['final_score'].round(1)
    
    # 5. Guardar dataset COMBINADO
    os.makedirs('data/processed', exist_ok=True)
    output_path = 'data/processed/combined_dataset.csv'
    combined_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    
    print(f"\n💾 DATASET COMBINADO GUARDADO:")
    print(f"   📁 {output_path}")
    print(f"   📊 {len(combined_df)} propiedades totales")
    
    # Estadísticas
    print("\n📈 ESTADÍSTICAS FINALES:")
    print(f"   Precio promedio: S/ {combined_df['price_soles'].mean():,.0f}")
    print(f"   Score promedio: {combined_df['final_score'].mean():.1f}/10")
    
    # Top propiedades
    print("\n🏆 TOP 3 PROPIEDADES (por score):")
    top3 = combined_df.nlargest(3, 'final_score')[['title', 'district', 'price_soles', 'final_score', 'source']]
    print(top3.to_string(index=False))
    
    return combined_df

if __name__ == "__main__":
    df = combine_datasets()