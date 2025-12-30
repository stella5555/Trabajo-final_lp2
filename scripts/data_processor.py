import pandas as pd
import os
import re

def clean_price(price_str):
    """Limpia y convierte precios a soles"""
    if pd.isna(price_str):
        return None

    price_str = str(price_str).upper().strip()

    # Extraer número
    number_match = re.search(r'(\d+\.?\d*)', price_str)
    if not number_match:
        return None

    value = float(number_match.group(1))

    # Detectar moneda
    if 'USD' in price_str:
        return value * 3.7  # tipo de cambio
    else:
        return value  # asumir soles

def clean_area(area_str):
    """Limpia el área y extrae el valor numérico"""
    if pd.isna(area_str):
        return None

    match = re.search(r'(\d+\.?\d*)', str(area_str))
    return float(match.group(1)) if match else None

def clean_bedroom_bathroom(value):
    """Convierte '2 dormitorios' o '3 baños' a int"""
    if pd.isna(value):
        return 1  # Valor por defecto
    
    value_str = str(value).strip()
    # Extraer el primer número
    match = re.search(r'(\d+)', value_str)
    if match:
        try:
            return int(match.group(1))
        except:
            return 1
    return 1

def extract_city_district(location):
    """
    Extrae ciudad y distrito de location de forma más robusta.
    """
    if pd.isna(location):
        return '', ''
    
    location_str = str(location).strip()
    
    # Separar por comas y limpiar
    parts = [p.strip() for p in location_str.split(',')]
    
    # Buscar patrones comunes
    for i, part in enumerate(parts):
        part_upper = part.upper()
        
        # Si encontramos un distrito conocido (lista de distritos de Lima)
        known_districts = [
            'MIRAFLORES', 'SAN ISIDRO', 'SURCO', 'LINCE', 'BARRANCO', 
            'LA MOLINA', 'SAN BORJA', 'JESUS MARIA', 'MAGDALENA',
            'PUEBLO LIBRE', 'SAN MIGUEL', 'ATE', 'LA VICTORIA',
            'BREÑA', 'RIMAC', 'LOS OLIVOS', 'SAN MARTIN DE PORRES',
            'SAN JUAN DE LURIGANCHO', 'SAN JUAN DE MIRAFLORES',
            'VILLA EL SALVADOR', 'CHORRILLOS', 'SAN LUIS'
        ]
        
        for dist in known_districts:
            if dist in part_upper:
                # El distrito es esta parte
                district = dist
                
                # La ciudad es Lima si está en el string
                city = 'LIMA' if 'LIMA' in location_str.upper() else parts[-1] if parts else ''
                
                return city.upper(), district
    
    # Si no encontramos un distrito conocido, usar la segunda parte
    district = parts[1] if len(parts) > 1 else ''
    city = parts[-1] if parts else ''
    
    # Limpiar texto
    district = district.upper().strip()
    city = city.upper().strip()
    
    # Corregir errores comunes
    if 'PROVINCIA' in district:
        # Buscar distrito real en otra parte
        for part in parts:
            part_upper = part.upper()
            for dist in known_districts:
                if dist in part_upper:
                    district = dist
                    break
    
    # Remover prefijos como "URB", "UR.", etc.
    district = re.sub(r'^(URB|UR\.|UR|AV\.|AV|CALLE|JR\.|JR)\s*', '', district, flags=re.IGNORECASE).strip()
    
    return city, district

def normalize_district_name(district):
    """Normaliza nombres de distritos para que coincidan con INEI"""
    if pd.isna(district):
        return ''
    
    district_str = str(district).upper().strip()
    
    # Correcciones específicas
    corrections = {
        'SAN MARTÍN DE PORRES': 'SAN MARTIN DE PORRES',
        'SAN MARTÍN': 'SAN MARTIN DE PORRES',
        'SANTIAGO DE SURCO': 'SURCO',
        'SURQUILLO': 'SURQUILLO',
        'JESÚS MARÍA': 'JESUS MARIA',
        'MAGDALENA DEL MAR': 'MAGDALENA DEL MAR',
        'CHACLACAYO': 'CHACLACAYO',
        'CIENEGUILLA': 'CIENEGUILLA',
        'PACHACAMAC': 'PACHACAMAC',
        'SANTA ANITA': 'SANTA ANITA',
        'VILLA MARÍA DEL TRIUNFO': 'VILLA MARIA DEL TRIUNFO',
        'SAN JUAN DE LURIGANCHO': 'SAN JUAN DE LURIGANCHO',
        'SAN JUAN DE MIRAFLORES': 'SAN JUAN DE MIRAFLORES',
        'COMAS': 'COMAS',
        'LOS OLIVOS': 'LOS OLIVOS',
        'INDEPENDENCIA': 'INDEPENDENCIA',
        'EL AGUSTINO': 'EL AGUSTINO',
        'ATE': 'ATE',
        'LA MOLINA': 'LA MOLINA',
        'SAN BORJA': 'SAN BORJA',
    }
    
    # Aplicar correcciones
    for wrong, correct in corrections.items():
        if wrong in district_str:
            return correct
    
    # Remover prefijos innecesarios
    district_str = re.sub(r'^(DISTRITO|DIST\.|DIST|URBANIZACIÓN|URB\.|URB|UR\.|UR)\s+', '', district_str)
    
    return district_str

def calculate_scores(df):
    """Aplica la fórmula de scoring adaptada al dataset de Properati Lima"""
    
    print("🔍 Procesando columnas:", df.columns.tolist())
    print(f"📊 Muestra de precios originales:\n{df['price'].head(10).tolist()}")
    
    # 1. LIMPIAR TODAS LAS COLUMNAS RELEVANTES
    print("🧹 Limpiando datos...")
    
    # Precio (convertir todo a soles)
    df['price_clean'] = df['price'].apply(clean_price)
    print(f"   Precios convertidos: {df['price_clean'].notna().sum()}/{len(df)} válidos")
    
    # Área
    df['area_clean'] = df['area'].apply(clean_area)
    print(f"   Áreas limpias: {df['area_clean'].notna().sum()}/{len(df)} válidas")
    
    # Dormitorios y baños
    df['bedroom_clean'] = df['bedroom'].apply(clean_bedroom_bathroom)
    df['bathroom_clean'] = df['bathroom'].apply(clean_bedroom_bathroom)
    
    # Año de construcción
    if 'year_contruction' in df.columns:
        df['year_contruction'] = pd.to_numeric(df['year_contruction'], errors='coerce')
    else:
        df['year_contruction'] = 1990

    # 2. COST_SCORE (40%) - Precio por m² normalizado
    print("💰 Calculando cost_score...")
    df['cost_score'] = 5.0  # Valor por defecto como float

    # Filtrar solo propiedades con precio y área válidos
    valid_mask = df['price_clean'].notna() & df['area_clean'].notna() & (df['area_clean'] > 0)
    valid_data = df[valid_mask].copy()

    if len(valid_data) > 0:
        # Calcular precio por m²
        valid_data['price_per_m2'] = valid_data['price_clean'] / valid_data['area_clean']
        
        # Normalizar a escala 0-10 (precio más bajo = score más alto)
        max_price_m2 = valid_data['price_per_m2'].max()
        if max_price_m2 > 0:
            valid_data['cost_score'] = (10 - (valid_data['price_per_m2'] / max_price_m2 * 10)).clip(0, 10)
        
        # Asegurar que cost_score sea float
        valid_data['cost_score'] = valid_data['cost_score'].astype(float)
        
        # Asignar de vuelta al DataFrame original
        df.loc[valid_data.index, 'cost_score'] = valid_data['cost_score']
    
    # 3. SAFETY_SCORE (40%) - Basado en seguridad por distrito
    print("🏙️ Calculando safety_score...")
    
    # Extraer ciudad y distrito
    print("📍 Extrayendo distritos de las ubicaciones...")
    df[['city', 'district']] = df['location'].apply(
        lambda x: pd.Series(extract_city_district(x))
    )
    
    # Aplicar normalización de nombres de distrito
    df['district'] = df['district'].apply(normalize_district_name)
    
    # Filtrar SOLO propiedades de Lima
    lima_mask = df['city'].str.contains('LIMA', case=False, na=False)
    print(f"   Propiedades en Lima: {lima_mask.sum()}/{len(df)}")
    
    df = df[lima_mask].copy()
    
    # Mostrar qué distritos tenemos
    unique_districts = df['district'].unique()
    print(f"📌 Distritos únicos encontrados: {len(unique_districts)}")
    print(f"   Ejemplos: {unique_districts[:10]}...")
    
    # Cargar seguridad por distrito y normalizar nombres también
    security_df = pd.read_csv("data/processed/security_by_district.csv")
    security_df["district"] = security_df["district"].apply(normalize_district_name)
    
    print(f"📌 Distritos en seguridad: {security_df['district'].unique()[:10]}...")
    
    # Hacer merge más inteligente
    df = pd.merge(
        df,
        security_df[["district", "security_score"]],
        on="district",
        how="left"
    )
    
    # Renombrar para consistencia
    df["safety_score"] = df["security_score"]
    
    # Ver cuántos coincidieron
    coincidencias = df["safety_score"].notna().sum()
    print(f"✅ Coincidencias con seguridad: {coincidencias}/{len(df)}")
    
    # Si no coincide, asignar puntaje por defecto
    df["safety_score"] = df["safety_score"].fillna(5)
    
    # Para debugging: mostrar los que no coincidieron
    if coincidencias < len(df):
        missing = df[df["safety_score"] == 5]["district"].unique()
        print(f"⚠️ Distritos sin match de seguridad ({len(missing)}):")
        print(f"   {missing[:10]}...")
    
    # 4. SERVICES_SCORE (20%) - Basado en características
    print("🛋️ Calculando services_score...")
    
    # Puntaje por tamaño
    size_score = (df['bedroom_clean'] + df['bathroom_clean']) * 1.5
    size_score = size_score.clip(0, 10)
    
    # Puntaje por antigüedad
    current_year = 2024
    age = current_year - df['year_contruction'].fillna(1990)
    age_score = (10 - (age / 50 * 10)).clip(0, 10)
    
    # Combinar servicios
    df['services_score'] = (size_score * 0.6 + age_score * 0.4).clip(0, 10)
    
    # 5. FÓRMULA FINAL (0.4/0.4/0.2)
    print("🎯 Calculando puntaje final...")
    df['final_score'] = (
        df['cost_score'] * 0.4 + 
        df['safety_score'] * 0.4 + 
        df['services_score'] * 0.2
    ).round(1)
    
    # Filtrar solo propiedades con datos válidos para mostrar
    valid_for_display = df.dropna(subset=['price_clean', 'area_clean'])
    
    # Ordenar de mejor a peor score
    return df.sort_values('final_score', ascending=False), valid_for_display

def main():
    print("📊 PROCESANDO DATOS DE PROPERTI LIMA...")
    print("="*60)
    
    try:
        # Cargar dataset de Properati
        df = pd.read_csv('data/raw/dataset.csv', encoding='utf-8')
        print(f"✅ Dataset cargado: {len(df)} propiedades")
        
        # Filtrar solo alquileres si es necesario
        if 'operation_type' in df.columns:
            alquileres = df[df['operation_type'].str.contains('alquiler', case=False, na=False)]
            print(f"🔍 Alquileres encontrados: {len(alquileres)}")
            df = alquileres  # Trabajar solo con alquileres
        
        # Calcular scores
        df_scored, valid_data = calculate_scores(df)
        
        # Guardar resultado CSV
        output_path = 'data/processed/scored_properties.csv'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df_scored.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        # Guardar JSON para frontend
        web_output = 'web/data/properties.json'
        os.makedirs(os.path.dirname(web_output), exist_ok=True)
        
        # Preparar datos para JSON (convertir NaN a None)
        json_data = df_scored.copy()
        
        # Seleccionar solo las columnas que necesitamos para el frontend
        columns_to_keep = [
            'title', 'location', 'price', 'bedroom', 'bathroom', 'area',
            'price_clean', 'area_clean', 'bedroom_clean', 'bathroom_clean',
            'cost_score', 'safety_score', 'security_score', 'services_score', 
            'final_score', 'district', 'city', 'operation_type', 'date_pub', 'url'
        ]
        
        # Filtrar columnas existentes
        columns_to_keep = [col for col in columns_to_keep if col in json_data.columns]
        json_data = json_data[columns_to_keep]
        
        # Convertir NaN a None para JSON
        json_data = json_data.where(pd.notna(json_data), None)
        
        # Convertir a JSON
        json_data.to_json(
            web_output,
            orient='records',
            force_ascii=False,
            indent=2
        )
        
        print(f"\n✅ PROCESAMIENTO COMPLETADO")
        print(f"📁 CSV guardado: {output_path}")
        print(f"🌐 JSON creado: {web_output}")
        print(f"📊 Propiedades procesadas: {len(df_scored)}")
        print(f"📊 Propiedades válidas: {len(valid_data)}")
        
        if len(valid_data) > 0:
            print(f"\n🏆 TOP 5 PROPIEDADES MEJOR PUNTAJE:")
            top5 = valid_data.sort_values('final_score', ascending=False).head()
            for idx, row in top5.iterrows():
                print(f"  {idx+1}. {row['district']} - S/. {row['price_clean']:.0f} - {row['area_clean']:.0f}m² - Score: {row['final_score']:.1f}")
            
            print("\n📊 ESTADÍSTICAS:")
            print(f"  • Precio promedio: S/. {valid_data['price_clean'].mean():.0f}")
            print(f"  • Área promedio: {valid_data['area_clean'].mean():.0f} m²")
            print(f"  • Puntaje promedio: {valid_data['final_score'].mean():.1f}")
            print(f"  • Score máximo: {valid_data['final_score'].max():.1f}")
            print(f"  • Score mínimo: {valid_data['final_score'].min():.1f}")
            
            # Estadísticas por distrito
            print(f"\n🏙️  DISTRITOS CON MÁS PROPIEDADES:")
            distrito_counts = valid_data['district'].value_counts().head(5)
            for distrito, count in distrito_counts.items():
                avg_score = valid_data[valid_data['district'] == distrito]['final_score'].mean()
                print(f"  • {distrito}: {count} propiedades, score promedio: {avg_score:.1f}")
        else:
            print("⚠️  No hay propiedades con datos completos de precio y área")
        
        return df_scored
        
    except FileNotFoundError as e:
        print(f"❌ Error: Archivo no encontrado - {e}")
        print("💡 Asegúrate de que 'data/raw/dataset.csv' existe")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()