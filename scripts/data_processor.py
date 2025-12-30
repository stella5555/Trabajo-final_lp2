# SOLO ESTA VERSIÓN - ELIMINA TODO LO DEMÁS
import pandas as pd
import os
import re

def clean_price(price_str):
    """Limpia y convierte precios a soles"""
    if pd.isna(price_str):
        return None
    
    price_str = str(price_str).upper().strip()
    
    # Extraer número (soporta comas como separadores de miles)
    number_match = re.search(r'[\d,]+\.?\d*', price_str.replace(',', ''))
    if not number_match:
        return None
    
    value = float(number_match.group(0).replace(',', ''))
    
    # Detectar moneda
    if 'USD' in price_str:
        return value * 3.7  # tipo de cambio
    else:
        return value  # asumir soles

def clean_area(area_str):
    """Limpia el área y extrae el valor numérico"""
    if pd.isna(area_str):
        return None
    
    # Buscar número (puede tener comas)
    match = re.search(r'[\d,]+\.?\d*', str(area_str).replace(',', ''))
    return float(match.group(0)) if match else None

def clean_bedroom_bathroom(value):
    """Convierte '2 dormitorios' o '3 baños' a int"""
    if pd.isna(value):
        return 1
    
    value_str = str(value).strip()
    match = re.search(r'(\d+)', value_str)
    return int(match.group(1)) if match else 1

def extract_district_from_location(location):
    """
    Extrae el distrito de una ubicación.
    Para Lima: 'Ur. Santa Cruz, Miraflores, Lima, Lima' → 'MIRAFLORES'
    Para otras ciudades: retorna None
    """
    if pd.isna(location):
        return None
    
    loc = str(location).strip().upper()
    
    # Patrón específico para Lima: algo, DISTRITO, Lima, Lima
    # Ejemplo: "Ur. Santa Cruz, Miraflores, Lima, Lima"
    pattern = r',\s*([A-ZÑÁÉÍÓÚ\s\-]+),\s*LIMA,\s*LIMA\s*$'
    match = re.search(pattern, loc)
    
    if match:
        district = match.group(1).strip()
        
        # Limpiar prefijos comunes
        district = re.sub(r'^(URB\.|URB|UR\.|UR|AV\.|AV|CALLE|JR\.|JR)\s+', '', district)
        
        # Corregir nombres específicos
        corrections = {
            'SANTIAGO DE SURCO': 'SURCO',
            'SAN MARTÍN DE PORRES': 'SAN MARTIN DE PORRES',
            'JESÚS MARÍA': 'JESUS MARIA',
            'MAGDALENA DEL MAR': 'MAGDALENA DEL MAR',
            'VILLA MARÍA DEL TRIUNFO': 'VILLA MARIA DEL TRIUNFO',
            'LURIGANCHO - CHOSICA': 'LURIGANCHO',
            'SANTA MARÍA DEL MAR': 'SANTA MARIA DEL MAR'
        }
        
        # Aplicar correcciones
        for wrong, correct in corrections.items():
            if wrong in district:
                district = district.replace(wrong, correct)
                break
        
        return district
    
    # Si no cumple el patrón de Lima, retornar None
    return None

def normalize_district_name(district):
    """Normaliza nombres de distritos para coincidir con security_by_district.csv"""
    if pd.isna(district):
        return None
    
    district_str = str(district).upper().strip()
    
    # Lista exacta de distritos en security_by_district.csv
    VALID_DISTRICTS = [
        'ANCON', 'ATE', 'BARRANCO', 'BREÑA', 'CARABAYLLO', 'CHACLACAYO',
        'CHORRILLOS', 'CIENEGUILLA', 'COMAS', 'EL AGUSTINO', 'INDEPENDENCIA',
        'JESUS MARIA', 'LA MOLINA', 'LA VICTORIA', 'LIMA', 'LINCE', 'LOS OLIVOS',
        'LURIGANCHO', 'LURIN', 'MAGDALENA DEL MAR', 'MIRAFLORES', 'PACHACAMAC',
        'PUEBLO LIBRE', 'PUENTE PIEDRA', 'RIMAC', 'SAN BARTOLO', 'SAN BORJA',
        'SAN ISIDRO', 'SAN JUAN DE LURIGANCHO', 'SAN JUAN DE MIRAFLORES',
        'SAN LUIS', 'SAN MARTIN DE PORRES', 'SAN MIGUEL', 'SANTA ANITA',
        'SANTA MARIA DEL MAR', 'SANTA ROSA', 'SURCO', 'SURQUILLO',
        'VILLA EL SALVADOR', 'VILLA MARIA DEL TRIUNFO', 'PUNTA HERMOSA',
        'PUNTA NEGRA', 'PUCUSANA'
    ]
    
    # Verificar si ya está en la lista
    if district_str in VALID_DISTRICTS:
        return district_str
    
    # Intentar mapear nombres similares
    mappings = {
        'SANTIAGO DE SURCO': 'SURCO',
        'LURIGANCHO - CHOSICA': 'LURIGANCHO',
        'SAN MARTÍN DE PORRES': 'SAN MARTIN DE PORRES',
        'JESÚS MARÍA': 'JESUS MARIA',
        'VILLA MARÍA DEL TRIUNFO': 'VILLA MARIA DEL TRIUNFO',
        'SANTA MARÍA DEL MAR': 'SANTA MARIA DEL MAR'
    }
    
    for wrong, correct in mappings.items():
        if wrong in district_str:
            return correct
    
    return None

def calculate_scores(df):
    """Calcula scores para propiedades de Lima"""
    
    print("🧹 Limpiando datos básicos...")
    
    # Limpiar datos básicos
    df['price_clean'] = df['price'].apply(clean_price)
    df['area_clean'] = df['area'].apply(clean_area)
    df['bedroom_clean'] = df['bedroom'].apply(clean_bedroom_bathroom)
    df['bathroom_clean'] = df['bathroom'].apply(clean_bedroom_bathroom)
    
    # Año de construcción (valor por defecto 2000 si no hay)
    if 'year_contruction' in df.columns:
        df['year_contruction'] = pd.to_numeric(df['year_contruction'], errors='coerce')
    df['year_contruction'] = df['year_contruction'].fillna(2000)
    
    print("📍 Extrayendo distritos...")
    
    # Extraer distritos
    df['district'] = df['location'].apply(extract_district_from_location)
    
    # Filtrar SOLO propiedades con distrito válido de Lima
    initial_count = len(df)
    df = df[df['district'].notna()].copy()
    print(f"   Propiedades con distrito de Lima: {len(df)}/{initial_count}")
    
    # Normalizar nombres de distrito
    df['district'] = df['district'].apply(normalize_district_name)
    
    # Cargar datos de seguridad
    security_df = pd.read_csv("data/processed/security_by_district.csv")
    security_df["district_norm"] = security_df["district"].apply(normalize_district_name)
    
    # Merge con seguridad
    df = pd.merge(
        df,
        security_df[["district_norm", "security_score"]].rename(columns={"district_norm": "district"}),
        on="district",
        how="left"
    )
    
    # Renombrar
    df["safety_score"] = df["security_score"]
    
    # Verificar merge
    matched = df['safety_score'].notna().sum()
    print(f"✅ Coincidencias con seguridad: {matched}/{len(df)}")
    
    if matched < len(df):
        missing = df[df['safety_score'].isna()]['district'].unique()
        print(f"⚠️  Distritos sin match: {missing}")
    
    # Rellenar valores faltantes
    df['safety_score'] = df['safety_score'].fillna(5.0)
    
    print("💰 Calculando cost_score...")
    
    # COST_SCORE: precio por m² normalizado (invertido: más barato = mejor score)
    df['cost_score'] = 5.0  # Valor por defecto
    
    # Solo para propiedades con precio y área válidos
    valid_mask = df['price_clean'].notna() & df['area_clean'].notna() & (df['area_clean'] > 0)
    valid_data = df[valid_mask].copy()
    
    if len(valid_data) > 0:
        valid_data['price_per_m2'] = valid_data['price_clean'] / valid_data['area_clean']
        max_price_m2 = valid_data['price_per_m2'].max()
        
        if max_price_m2 > 0:
            # Normalizar: precio más bajo = score más alto
            valid_data['cost_score'] = 10 * (1 - valid_data['price_per_m2'] / max_price_m2)
            valid_data['cost_score'] = valid_data['cost_score'].clip(0, 10)
        
        df.loc[valid_data.index, 'cost_score'] = valid_data['cost_score']
    
    print("🛋️ Calculando services_score...")
    
    # SERVICES_SCORE: basado en características de la propiedad
    # 1. Puntaje por tamaño (más habitaciones y baños = mejor)
    size_score = (df['bedroom_clean'] + df['bathroom_clean']) * 1.5
    size_score = size_score.clip(0, 10)
    
    # 2. Puntaje por antigüedad (más nuevo = mejor)
    current_year = 2024
    age = current_year - df['year_contruction']
    age_score = 10 * (1 - age / 100)  # Propiedades de 100 años tendrían score 0
    age_score = age_score.clip(0, 10)
    
    # 3. Combinar
    df['services_score'] = (size_score * 0.6 + age_score * 0.4).clip(0, 10)
    
    print("🎯 Calculando score final...")
    
    # FÓRMULA FINAL: (Costo×0.4) + (Seguridad×0.4) + (Servicios×0.2)
    df['final_score'] = (
        df['cost_score'] * 0.4 + 
        df['safety_score'] * 0.4 + 
        df['services_score'] * 0.2
    ).round(2)
    
    # Ordenar por score
    df = df.sort_values('final_score', ascending=False)
    
    # Filtrar propiedades válidas para mostrar
    valid_for_display = df[
        df['price_clean'].notna() & 
        df['area_clean'].notna() & 
        (df['area_clean'] > 0)
    ].copy()
    
    return df, valid_for_display

def main():
    print("="*60)
    print("🏡 LIMA HOUSING ANALYTICS - PROCESADOR FINAL")
    print("="*60)
    
    try:
        # Cargar datos
        print("\n📥 Cargando dataset...")
        df = pd.read_csv('data/raw/dataset.csv', encoding='utf-8')
        print(f"   Total propiedades en dataset: {len(df)}")
        
        # Filtrar solo alquileres
        if 'operation_type' in df.columns:
            df = df[df['operation_type'].str.contains('alquiler', case=False, na=False)]
            print(f"   Alquileres encontrados: {len(df)}")
        
        # Calcular scores
        df_scored, valid_data = calculate_scores(df)
        
        print(f"\n📊 RESULTADOS:")
        print(f"   • Propiedades procesadas: {len(df_scored)}")
        print(f"   • Propiedades válidas para mostrar: {len(valid_data)}")
        
        # Guardar CSV
        output_csv = 'data/processed/scored_properties.csv'
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        df_scored.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"✅ CSV guardado: {output_csv}")
        
        # Preparar JSON para frontend
        print("\n🔄 Preparando JSON para frontend...")
        
        # Seleccionar columnas importantes
        columns_for_json = [
            'title', 'location', 'district',
            'price_clean', 'area_clean', 
            'bedroom_clean', 'bathroom_clean',
            'cost_score', 'safety_score', 'services_score', 'final_score',
            'date_pub', 'url'
        ]
        
        # Filtrar columnas existentes
        columns_for_json = [col for col in columns_for_json if col in df_scored.columns]
        json_data = df_scored[columns_for_json].copy()
        
        # Convertir NaN a None
        json_data = json_data.where(pd.notna(json_data), None)
        
        # Guardar JSON
        output_json = 'web/data/properties.json'
        os.makedirs(os.path.dirname(output_json), exist_ok=True)
        
        with open(output_json, 'w', encoding='utf-8') as f:
            json_data.to_json(f, orient='records', force_ascii=False, indent=2)
        
        print(f"✅ JSON guardado: {output_json}")
        print(f"   Propiedades en JSON: {len(json_data)}")
        
        # Mostrar estadísticas
        if len(valid_data) > 0:
            print(f"\n🏆 TOP 5 PROPIEDADES (MEJOR SCORE):")
            top5 = valid_data.head(5)
            for i, (_, row) in enumerate(top5.iterrows(), 1):
                print(f"   {i}. {row['district']} - S/. {row['price_clean']:.0f} - {row['area_clean']:.0f}m²")
                print(f"      Score: {row['final_score']:.1f} (Costo:{row['cost_score']:.1f}, Seg:{row['safety_score']:.1f}, Serv:{row['services_score']:.1f})")
            
            print(f"\n📈 ESTADÍSTICAS GENERALES:")
            print(f"   • Precio promedio: S/. {valid_data['price_clean'].mean():.0f}")
            print(f"   • Área promedio: {valid_data['area_clean'].mean():.0f} m²")
            print(f"   • Score promedio: {valid_data['final_score'].mean():.1f}")
            
            print(f"\n🏙️  DISTRITOS CON MÁS PROPIEDADES:")
            district_stats = valid_data['district'].value_counts().head(5)
            for distrito, count in district_stats.items():
                avg_price = valid_data[valid_data['district'] == distrito]['price_clean'].mean()
                avg_score = valid_data[valid_data['district'] == distrito]['final_score'].mean()
                print(f"   • {distrito}: {count} propiedades")
                print(f"     Precio avg: S/. {avg_price:.0f}, Score avg: {avg_score:.1f}")
        
        print(f"\n🎉 PROCESAMIENTO COMPLETADO!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()