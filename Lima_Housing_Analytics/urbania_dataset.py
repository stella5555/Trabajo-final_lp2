import pandas as pd

# 1. CARGAMOS EL DATASET "dataset_final.csv"
try:
    # Leemos el archivo asegurando que se entiendan los caracteres especiales (utf-8)
    df = pd.read_csv('dataset_final.csv', encoding='utf-8')
    print("✅ Dataset cargado: 120 propiedades listas para comparar.")
except FileNotFoundError:
    print("⚠️ Error: No encuentro 'dataset_final.csv'. Asegúrate de que esté junto a app.py")
    df = pd.DataFrame() # Creamos vacío para evitar errores

def evaluar_precio_mercado(distrito_usuario, precio_m2_usuario, habitaciones_usuario):
    """
    Retorna una nota del 0 al 10.
    """
    if df.empty:
        return 5.0 # Nota neutral si falla la carga

    # 2. FILTROS INTELIGENTES
    # Convertimos a mayúsculas para que 'Ate' coincida con 'ATE' o 'ate'
    filtro_distrito = df['district'].str.upper() == distrito_usuario.upper()
    
    # Buscamos dptos con habitaciones similares (+/- 1 habitación de diferencia)
    filtro_hab = (df['bedrooms'] >= habitaciones_usuario - 1) & \
                 (df['bedrooms'] <= habitaciones_usuario + 1)
    
    # Aplicamos los filtros
    data_comparable = df[filtro_distrito & filtro_hab]

    # Si no encontramos nada exacto, intentamos filtrar SOLO por distrito (más general)
    if data_comparable.empty:
        data_comparable = df[filtro_distrito]
    
    # Si aun así no hay nada (ej: un distrito que no está en el excel), devolvemos 5
    if data_comparable.empty:
        print(f"⚠️ No hay datos históricos para {distrito_usuario}.")
        return 5.0

    # 3. CALCULAMOS EL PROMEDIO DE MERCADO
    # Usamos la columna 'price_per_m2'
    precio_mercado_promedio = data_comparable['price_per_m2'].mean()

    print(f"📊 Mercado en {distrito_usuario}: S/.{round(precio_mercado_promedio, 2)}/m2 vs Usuario: S/.{precio_m2_usuario}/m2")

    # 4. ALGORITMO DE NOTA (Si es más barato que el mercado = Mejor Nota)
    
    # Calculamos qué tan diferente es el precio del usuario vs el mercado
    diferencia = (precio_m2_usuario - precio_mercado_promedio) / precio_mercado_promedio

    # Si es 30% más barato (o más) -> Nota 10 (¡Ofertón!)
    if diferencia <= -0.30:
        return 10.0
    
    # Si es 30% más caro (o más) -> Nota 0 (Muy caro)
    elif diferencia >= 0.30:
        return 0.0
    
    # Casos intermedios: Calculamos proporcionalmente
    else:
        # Empieza en 5. Sube si es barato (diferencia negativa), baja si es caro.
        nota = 5 - (diferencia * 10) 
        return max(0, min(10, round(nota, 2))) # Aseguramos que esté entre 0 y 10