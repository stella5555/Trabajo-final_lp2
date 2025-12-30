import googlemaps
# ---------------------------------------------------------
# PARTE 1: CONFIGURACIÓN
# ---------------------------------------------------------
# Colocamos nuestra API key
API_KEY = 'AIzaSyA9yU8036YYM6pXyYOPAHEsV-AUJKT2YYU'
gmaps = googlemaps.Client(key=API_KEY)

# ---------------------------------------------------------
# PARTE 2: LAS FUNCIONES 
# ---------------------------------------------------------

def obtener_coordenadas_de_nombre(nombre_lugar):
    """ Convierte un nombre (ej. 'Plaza de Armas') en coordenadas. """
    print(f"🔎 Buscando coordenadas para: '{nombre_lugar}'...")
    respuesta = gmaps.geocode(nombre_lugar)
    
    if respuesta:
        ubicacion = respuesta[0]['geometry']['location']
        direccion = respuesta[0]['formatted_address']
        print(f"📍 Dirección encontrada: {direccion}")
        return ubicacion['lat'], ubicacion['lng']
    else:
        print("❌ No se encontró el lugar.")
        return None, None

def calcular_nota_servicios(parques, transporte, restaurantes):

    # 1. TRANSPORTE (Max 4 puntos) 
    if transporte >= 8:
        nota_transporte = 4.0
    else:
        nota_transporte = transporte * 0.5 

    # 2. PARQUES (Max 3 puntos) 
    if parques > 3: 
        nota_parques = 3.0
    else:
        nota_parques = parques * 0.75 
        
    # 3. RESTAURANTES (Max 3 puntos) 
    if restaurantes >= 5:
        nota_restaurantes = 3.0
    else:
        nota_restaurantes = restaurantes * 0.6

    return nota_transporte + nota_parques + nota_restaurantes

# Solo la nota de comisaría
def calcular_nota_seguridad(policia):
 # 1. COMISARÍA (Max 3 puntos)
    if policia >= 1:
        return 10.0
    else:
        return 0.0

def analizar_zona_google(lat, lon):

    print("📊 Analizando el entorno (500m a la redonda)...")
    
    # --- A. OBTENCIÓN DE DATOS (API) ---
    
    # 1. Restaurantes
    res_restaurantes = gmaps.places_nearby(location=(lat, lon), radius=500, type='restaurant')
    num_restaurantes = len(res_restaurantes.get('results', []))

    # 2. Parques
    res_parques = gmaps.places_nearby(location=(lat, lon), radius=500, type='park')
    num_parques = len(res_parques.get('results', []))
    
    # 3. Policía (Seguridad) - Radio 1km
    res_policia = gmaps.places_nearby(location=(lat, lon), radius=1000, type='police')
    num_policia = len(res_policia.get('results', []))

    # 4. Transporte
    res_transporte = gmaps.places_nearby(location=(lat, lon), radius=500, type='transit_station')
    num_transporte = len(res_transporte.get('results', []))

    # --- B. CÁLCULO DE NOTA  ---
    
    puntaje_calculado = (calcular_nota_servicios(num_parques, num_transporte, num_restaurantes)*0.2)
    puntaje_policia = (calcular_nota_seguridad(num_policia)*0.08)

    # --- C. RESULTADO FINAL SERVICIOS (20%) ---
    return {
        "cantidades": {
            "restaurantes": num_restaurantes,
            "parques": num_parques,
            "policia": num_policia,
            "transporte": num_transporte
        },
        "puntaje_total": round(puntaje_calculado, 2),
        # --- C.2 RESULTADO FINAL COMISARÍA (8%) ---
        "puntaje_total_policia": round(puntaje_policia, 2)
    }

# ---------------------------------------------------------
# PARTE 3: EJECUCIÓN
# ---------------------------------------------------------

# 1. Se escribe aquí el lugar que queremos probar
mi_lugar = "Ceres, Ate" 

# 2. Obtenemos coordenadas
lat, lon = obtener_coordenadas_de_nombre(mi_lugar)

# 3. Se analizan las coordenadas
if lat and lon:
    resultados = analizar_zona_google(lat, lon)
    
    print("\n" + "="*60)
    print(f"   ANÁLISIS DE SERVICIOS (20% del total): {mi_lugar}")
    print("="*60)
    print(f"🚌 Transporte:    {resultados['cantidades']['transporte']}")
    print(f"🌳 Parques:       {resultados['cantidades']['parques']}")
    print(f"🍽️ Restaurantes:  {resultados['cantidades']['restaurantes']}")
    print("-" * 60)
    print(f"⭐ NOTA FINAL:    {resultados['puntaje_total']}")
    print("="*60)

    print("="*60)
    print("--- 🛡️ BLOQUE SEGURIDAD ( 8% del total del 40% de SEGURIDAD) ---")
    print(f"👮 Comisarías:    {resultados['cantidades']['policia']} encontradas (1km)")
    print("-" * 60)
    print(f"👉 NOTA INFRAESTRUCTURA POLICIAL: {resultados['puntaje_total_policia']}")
    print("="*60)