import pandas as pd
import os
import re

def clean_price(price_str):
    """
    Convierte precios como 'USD900', 'S/.3,100' o 'S/.1,800' a float (en soles)
    """
    if pd.isna(price_str):
        return None
    
    price_str = str(price_str).strip()
    
    # Caso 1: USD (convertir a soles)
    if 'USD' in price_str:
        price_str = price_str.replace('USD', '').replace(',', '')
        try:
            return float(price_str) * 3.7  # Tipo de cambio aprox
        except:
            return None
    
    # Caso 2: Soles (S/. o S/)
    elif 'S/.' in price_str or 'S/' in price_str:
        price_str = re.sub(r'S/\.?\s*', '', price_str)  # Remover S/. o S/
        price_str = price_str.replace(',', '')
        try:
            return float(price_str)
        except:
            return None
    
    # Caso 3: Solo números (intentar convertir)
    else:
        try:
            return float(str(price_str).replace(',', ''))
        except:
            return None

def clean_area(area_str):
    """
    Convierte área como '103 mÂ²' o '151 m²' a float
    """
    if pd.isna(area_str):
        return None
    
    area_str = str(area_str).strip()
    # Extraer solo los números (y punto decimal)
    match = re.search(r'(\d+\.?\d*)', area_str)
    if match:
        try:
            return float(match.group(1))
        except:
            return None
    return None

def clean_bedroom_bathroom(value):
    """
    Convierte '2 dormitorios' o '3 baÃ±os' a int
    """
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
    df['year_contruction'] = pd.to_numeric(df['year_contruction'], errors='coerce')
    
    # 2. COST_SCORE (40%) - Precio por m² normalizado
    print("💰 Calculando cost_score...")
    
    # Filtrar solo propiedades con precio y área válidos
    valid_data = df.dropna(subset=['price_clean', 'area_clean'])
    valid_data = valid_data[valid_data['area_clean'] > 0]  # Área positiva
    
    if len(valid_data) > 0:
        # Calcular precio por m²
        valid_data.loc[:, 'price_per_m2'] = valid_data['price_clean'] / valid_data['area_clean']
        
        # Normalizar a escala 0-10 (precio más bajo = score más alto)
        max_price_m2 = valid_data['price_per_m2'].max()
        valid_data.loc[:, 'cost_score'] = (10 - (valid_data['price_per_m2'] / max_price_m2 * 10)).clip(0, 10)
        
        # Asignar de vuelta al DataFrame original
        df.loc[valid_data.index, 'cost_score'] = valid_data['cost_score']
    
    # Rellenar NaN con valor promedio (5)
    df['cost_score'] = df['cost_score'].fillna(5)
    
    # 3. SAFETY_SCORE (40%) - Basado en ubicación
    print("🏙️ Calculando safety_score...")
    
    # Extraer ciudad de location (para filtrar solo Lima)
    df['city'] = df['location'].apply(lambda x: str(x).split(',')[-2].strip() if pd.notna(x) else '')
    df['district'] = df['location'].apply(lambda x: str(x).split(',')[-3].strip() if pd.notna(x) and len(str(x).split(',')) >= 3 else '')
    
    # Mapa de seguridad por distrito de Lima (AJUSTA SEGÚN TU CONOCIMIENTO)
    safety_by_district = {
        'Miraflores': 9, 'San Isidro': 9, 'La Molina': 9,
        'Barranco': 8, 'Surco': 8, 'San Borja': 8,
        'Lince': 7, 'Jesus Maria': 7, 'Magdalena': 7,
        'San Miguel': 6, 'Pueblo Libre': 6, 'Surquillo': 6,
        'Breña': 5, 'Rimac': 4, 'Cercado de Lima': 4,
        'San Juan de Lurigancho': 3, 'Comas': 3, 'Villa El Salvador': 3
    }
    
    # Solo propiedades de Lima tienen safety_score alto
    df['safety_score'] = 3  # Valor base bajo para no-Lima
    df.loc[df['city'] == 'Lima', 'safety_score'] = 5  # Valor medio para Lima genérico
    
    # Asignar valores específicos por distrito
    for district, score in safety_by_district.items():
        df.loc[df['district'] == district, 'safety_score'] = score
    
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
        
        # Guardar resultado
        output_path = 'data/processed/scored_properties.csv'
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df_scored.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        print(f"✅ Scores calculados para {len(df_scored)} propiedades")
        print(f"📁 Resultados guardados en: {output_path}")
        
        if len(valid_data) > 0:
            print(f"📊 Propiedades con datos completos: {len(valid_data)}")
            print("\n🏆 TOP 5 PROPIEDADES MEJOR PUNTAJE (CON DATOS COMPLETOS):")
            top5 = valid_data.sort_values('final_score', ascending=False).head()
            print(top5[['location', 'price_clean', 'area_clean', 'bedroom_clean', 'final_score']].to_string())
            
            print("\n📊 ESTADÍSTICAS:")
            print(f"  Precio promedio: S/. {valid_data['price_clean'].mean():.0f}")
            print(f"  Área promedio: {valid_data['area_clean'].mean():.0f} m²")
            print(f"  Puntaje máximo: {valid_data['final_score'].max():.1f}")
            print(f"  Puntaje mínimo: {valid_data['final_score'].min():.1f}")
            print(f"  Puntaje promedio: {valid_data['final_score'].mean():.1f}")
        else:
            print("⚠️  No hay propiedades con datos completos de precio y área")
        
        return df_scored
        
    except FileNotFoundError:
        print("❌ Error: No se encontró 'data/raw/dataset.csv'")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()