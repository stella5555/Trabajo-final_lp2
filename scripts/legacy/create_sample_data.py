# scripts/create_sample_data.py
import pandas as pd
import numpy as np
import os
from datetime import datetime

def create_realistic_sample_dataset():
    """
    Crea un dataset de muestra REALISTA para Lima
    Basado en precios reales del mercado y características de distritos
    """
    print("="*70)
    print("🏗️  CREANDO DATASET DE MUESTRA REALISTA PARA LIMA")
    print("="*70)
    
    # Configurar semilla para reproducibilidad
    np.random.seed(42)
    
    # ========================
    # 1. DATOS BASE POR DISTRITO
    # ========================
    # Basado en investigación real de precios en Lima 2024
    districts_info = {
        'Miraflores': {
            'price_range': (2500, 6000),
            'area_range': (45, 120),
            'safety_base': 8.5,
            'services_base': 9.0,
            'lat_range': (-12.118, -12.122),
            'lon_range': (-77.028, -77.032),
            'description': 'Zona turística y comercial exclusiva'
        },
        'Surco': {
            'price_range': (1800, 4500),
            'area_range': (50, 110),
            'safety_base': 8.0,
            'services_base': 8.5,
            'lat_range': (-12.115, -12.125),
            'lon_range': (-77.008, -77.015),
            'description': 'Residencial con amplias áreas verdes'
        },
        'San Isidro': {
            'price_range': (3000, 7000),
            'area_range': (55, 130),
            'safety_base': 9.0,
            'services_base': 9.5,
            'lat_range': (-12.095, -12.105),
            'lon_range': (-77.035, -77.045),
            'description': 'Distrito financiero y empresarial'
        },
        'Barranco': {
            'price_range': (1500, 3800),
            'area_range': (40, 90),
            'safety_base': 7.5,
            'services_base': 8.0,
            'lat_range': (-12.145, -12.155),
            'lon_range': (-77.020, -77.025),
            'description': 'Zona bohemia y cultural'
        },
        'La Molina': {
            'price_range': (2000, 5000),
            'area_range': (60, 140),
            'safety_base': 8.8,
            'services_base': 8.0,
            'lat_range': (-12.075, -12.085),
            'lon_range': (-76.945, -76.955),
            'description': 'Zona residencial familiar'
        },
        'Jesus Maria': {
            'price_range': (1300, 3200),
            'area_range': (42, 85),
            'safety_base': 7.0,
            'services_base': 7.5,
            'lat_range': (-12.075, -12.085),
            'lon_range': (-77.045, -77.055),
            'description': 'Céntrico y bien conectado'
        },
        'Lince': {
            'price_range': (1100, 2800),
            'area_range': (38, 75),
            'safety_base': 6.5,
            'services_base': 7.0,
            'lat_range': (-12.085, -12.095),
            'lon_range': (-77.030, -77.040),
            'description': 'Distrito tradicional céntrico'
        },
        'San Miguel': {
            'price_range': (1200, 3000),
            'area_range': (40, 80),
            'safety_base': 6.8,
            'services_base': 7.2,
            'lat_range': (-12.075, -12.085),
            'lon_range': (-77.090, -77.100),
            'description': 'Universidades y vida nocturna'
        },
        'Magdalena': {
            'price_range': (1250, 3100),
            'area_range': (41, 82),
            'safety_base': 7.2,
            'services_base': 7.0,
            'lat_range': (-12.095, -12.105),
            'lon_range': (-77.065, -77.075),
            'description': 'Cerca al mar y malecones'
        },
        'Pueblo Libre': {
            'price_range': (1000, 2600),
            'area_range': (35, 70),
            'safety_base': 7.0,
            'services_base': 6.8,
            'lat_range': (-12.070, -12.080),
            'lon_range': (-77.060, -77.070),
            'description': 'Histórico y tranquilo'
        }
    }
    
    # ========================
    # 2. GENERAR PROPIEDADES
    # ========================
    all_properties = []
    property_id = 1000
    
    for district, info in districts_info.items():
        # Número de propiedades por distrito (8-15)
        n_props = np.random.randint(8, 16)
        
        for i in range(n_props):
            property_id += 1
            
            # ===== PRECIO (distribución normal realista) =====
            min_price, max_price = info['price_range']
            mean_price = (min_price + max_price) / 2
            std_price = (max_price - min_price) / 4  # Desviación estándar
            
            price = np.random.normal(mean_price, std_price)
            # Asegurar dentro del rango realista
            price = np.clip(price, min_price * 0.9, max_price * 1.1)
            price = int(round(price / 50) * 50)  # Redondear a múltiplos de 50
            
            # ===== ÁREA (correlacionada con precio) =====
            # Relación aproximada: ~S/ 40-60 por m²
            base_area = price / np.random.uniform(40, 60)
            
            # Añadir variación
            area_variation = np.random.uniform(0.8, 1.2)
            area = base_area * area_variation
            
            # Asegurar dentro del rango del distrito
            min_area, max_area = info['area_range']
            area = np.clip(area, min_area, max_area)
            area = round(area, 1)
            
            # ===== HABITACIONES Y BAÑOS =====
            if area < 50:
                bedrooms = 1
            elif area < 70:
                bedrooms = 2
            elif area < 90:
                bedrooms = np.random.choice([2, 3], p=[0.6, 0.4])
            else:
                bedrooms = np.random.choice([3, 4], p=[0.7, 0.3])
            
            bathrooms = max(1, bedrooms - np.random.choice([0, 1], p=[0.8, 0.2]))
            
            # ===== PUNTAJES DE SEGURIDAD Y SERVICIOS =====
            # Base del distrito + variación individual
            safety_score = info['safety_base'] + np.random.uniform(-0.5, 0.3)
            services_score = info['services_base'] + np.random.uniform(-0.4, 0.4)
            
            # Asegurar dentro de rango 0-10
            safety_score = np.clip(safety_score, 5.0, 10.0)
            services_score = np.clip(services_score, 5.0, 10.0)
            
            # ===== PRECIO POR M² =====
            price_per_m2 = price / area if area > 0 else 0
            
            # ===== SCORE DE COSTO (tu fórmula) =====
            # Menor precio por m² = mejor score (máx 10, mín 0)
            cost_score = 10 - (price_per_m2 / 100)
            cost_score = np.clip(cost_score, 0, 10)
            
            # ===== SCORE FINAL (tu fórmula: 40/40/20) =====
            final_score = (
                cost_score * 0.4 + 
                safety_score * 0.4 + 
                services_score * 0.2
            )
            
            # ===== DIRECCIÓN REALISTA =====
            street_types = ['Av.', 'Calle', 'Jr.', 'Psje.']
            street_names = ['Arequipa', 'Javier Prado', 'Salaverry', 'Angamos', 
                           'Benavides', 'La Mar', 'Alcanfores', 'Larco', 'Schell']
            
            address = (
                f"{np.random.choice(street_types)} "
                f"{np.random.choice(street_names)} "
                f"{np.random.randint(100, 2000)}, {district}"
            )
            
            # ===== COORDENADAS GEOGRÁFICAS REALES =====
            latitude = np.random.uniform(info['lat_range'][0], info['lat_range'][1])
            longitude = np.random.uniform(info['lon_range'][0], info['lon_range'][1])
            
            # ===== CONSTRUIR REGISTRO =====
            property_data = {
                'id': f"PROP{property_id:04d}",
                'district': district,
                'address': address,
                'description': info['description'],
                'price_soles': int(price),
                'area_m2': area,
                'price_per_m2': round(price_per_m2, 2),
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'safety_score': round(safety_score, 1),
                'services_score': round(services_score, 1),
                'cost_score': round(cost_score, 1),
                'final_score': round(final_score, 1),
                'latitude': round(latitude, 6),
                'longitude': round(longitude, 6),
                'parking': np.random.choice([0, 1], p=[0.3, 0.7]),
                'furnished': np.random.choice([0, 1], p=[0.6, 0.4]),
                'pet_friendly': np.random.choice([0, 1], p=[0.4, 0.6]),
                'created_date': datetime.now().strftime('%Y-%m-%d'),
                'source': 'sample_data'
            }
            
            all_properties.append(property_data)
    
    # ========================
    # 3. CREAR DATAFRAME
    # ========================
    df = pd.DataFrame(all_properties)
    
    # Ordenar por score final (mejores primero)
    df = df.sort_values('final_score', ascending=False).reset_index(drop=True)
    
    # ========================
    # 4. GUARDAR ARCHIVOS
    # ========================
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    
    # Guardar en múltiples formatos
    raw_path = 'data/raw/sample_properties_detailed.csv'
    processed_path = 'data/processed/dataset_final.csv'
    
    df.to_csv(raw_path, index=False, encoding='utf-8-sig')
    df.to_csv(processed_path, index=False, encoding='utf-8-sig')
    
    print(f"\n✅ DATASET CREADO EXITOSAMENTE")
    print("="*70)
    print(f"📊 PROPIEDADES TOTALES: {len(df)}")
    print(f"🏙️  DISTRITOS INCLUIDOS: {df['district'].nunique()}")
    print(f"💰 PRECIO PROMEDIO: S/ {df['price_soles'].mean():,.0f}")
    print(f"📐 ÁREA PROMEDIO: {df['area_m2'].mean():.1f} m²")
    print(f"⭐ SCORE PROMEDIO: {df['final_score'].mean():.1f}/10")
    
    # ========================
    # 5. ANÁLISIS POR DISTRITO
    # ========================
    print("\n📈 ANÁLISIS POR DISTRITO:")
    print("-"*70)
    
    district_stats = []
    for district in df['district'].unique():
        dist_df = df[df['district'] == district]
        stats = {
            'Distrito': district,
            'Props': len(dist_df),
            'Precio Avg': f"S/ {dist_df['price_soles'].mean():,.0f}",
            'Área Avg': f"{dist_df['area_m2'].mean():.0f} m²",
            'Score Avg': f"{dist_df['final_score'].mean():.1f}",
            'Mejor Score': f"{dist_df['final_score'].max():.1f}"
        }
        district_stats.append(stats)
    
    # Mostrar tabla
    stats_df = pd.DataFrame(district_stats)
    print(stats_df.to_string(index=False))
    
    # ========================
    # 6. MEJORES OFERTAS
    # ========================
    print("\n🏆 TOP 5 MEJORES OFERTAS (Relación Calidad-Precio):")
    print("-"*70)
    
    # Calcular relación score/precio
    df['value_ratio'] = df['final_score'] / (df['price_soles'] / 1000)
    top5 = df.nlargest(5, 'value_ratio')[[
        'district', 'address', 'price_soles', 'area_m2', 'final_score', 'value_ratio'
    ]]
    
    for idx, row in top5.iterrows():
        print(f"📍 {row['district']:15} | S/ {row['price_soles']:>6,} | "
              f"{row['area_m2']:>4.0f} m² | Score: {row['final_score']:>4.1f} | "
              f"Valor: {row['value_ratio']:.2f}")
    
    # ========================
    # 7. ARCHIVOS GUARDADOS
    # ========================
    print("\n💾 ARCHIVOS GUARDADOS:")
    print("-"*70)
    print(f"📁 Datos crudos: {raw_path}")
    print(f"📁 Dataset final: {processed_path}")
    print(f"📁 Tamaño total: {os.path.getsize(processed_path) / 1024:.1f} KB")
    
    # ========================
    # 8. EJEMPLO DE PROPIEDAD
    # ========================
    print("\n📄 EJEMPLO DE UNA PROPIEDAD (la #1 por score):")
    print("-"*70)
    best_property = df.iloc[0]
    
    example = f"""
    🏡 ID: {best_property['id']}
    📍 Distrito: {best_property['district']}
    🏠 Dirección: {best_property['address']}
    💰 Precio: S/ {best_property['price_soles']:,}
    📐 Área: {best_property['area_m2']} m² (S/ {best_property['price_per_m2']}/m²)
    🛏️  Habitaciones: {best_property['bedrooms']} | 🛁 Baños: {best_property['bathrooms']}
    ⭐ Puntajes:
       • Seguridad: {best_property['safety_score']}/10
       • Servicios: {best_property['services_score']}/10  
       • Costo: {best_property['cost_score']}/10
       • FINAL: {best_property['final_score']}/10 🏆
    📍 Ubicación: {best_property['latitude']}, {best_property['longitude']}
    """
    print(example)
    
    print("\n" + "="*70)
    print("🎯 DATASET LISTO PARA ANÁLISIS Y DASHBOARD")
    print("="*70)
    
    return df

if __name__ == "__main__":
    df = create_realistic_sample_dataset()