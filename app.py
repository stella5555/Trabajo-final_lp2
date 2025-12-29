from flask import Flask, render_template, request
import mis_modulos

app = Flask(__name__)

# ============================================
# 1. DATOS COMPLEMENTARIOS
# ============================================

# Base de datos manual de seguridad ciudadana (INEI)
# Estos valores representan el "Riesgo Social"
bd_seguridad_inei = {
    "SAN ISIDRO": 9.5, "MIRAFLORES": 8.5, "SAN BORJA": 9.0,
    "LA MOLINA": 8.5, "MAGDALENA": 8.0, "JESUS MARIA": 7.8,
    "SURCO": 7.0, "SAN MIGUEL": 6.8, "CERCADO DE LIMA": 5.0,
    "ATE": 4.5, "SANTA ANITA": 4.5, "LOS OLIVOS": 4.5,
    "SAN JUAN DE LURIGANCHO": 3.0, "CALLAO": 3.0,
    "LINCE": 6.5, "PUEBLO LIBRE": 7.5, "BARRANCO": 7.0
}

def obtener_nota_inei(distrito):
    """Devuelve la nota del 0 al 10 según el distrito"""
    return bd_seguridad_inei.get(distrito.upper(), 5.0)

def calcular_nota_precio(precio_m2):
    """
    Calcula nota del 0 al 10 según el precio.
    Mientras más barato, mejor nota (oportunidad).
    """
    if precio_m2 <= 1000: return 10.0
    elif precio_m2 <= 1300: return 9.0
    elif precio_m2 <= 1600: return 7.5
    elif precio_m2 <= 2000: return 5.0
    elif precio_m2 <= 2500: return 3.0
    else: return 1.0

# ============================================
# 2. EL CEREBRO DE LA PÁGINA
# ============================================

@app.route('/', methods=['GET', 'POST'])
def home():
    datos_resultado = None
    notas_visuales = None
    detalles_api = None

    if request.method == 'POST':
        # 1. Recibir datos del HTML
        lugar = request.form['lugar']
        distrito = request.form['distrito']
        try:
            precio = float(request.form['precio'])
        except ValueError:
            precio = 0.0

        # 2. Llamar a TU módulo (Google Maps)
        lat, lon = mis_modulos.obtener_coordenadas_de_nombre(lugar)
        
        if lat:
            # Esto devuelve el diccionario de mis_modulos
            resultados_google = mis_modulos.analizar_zona_google(lat, lon)
            
            # --- A. RECUPERAR TUS PUNTAJES PONDERADOS ---
            # Servicios ya viene multiplicado por 0.20
            score_servicios_ponderado = resultados_google['puntaje_total']
            
            # Infraestructura (Comisaría) ya viene multiplicada por 0.08
            score_policia_ponderado = resultados_google['puntaje_total_policia']

            # --- B. CALCULAR LO QUE FALTA ---
            
            # 1. SEGURIDAD SOCIAL (INEI)
            # La seguridad total vale 40%.
            # La comisaría ya cubrió el 20% de eso (es decir, un 8% total).
            # El INEI debe cubrir el 80% restante de la seguridad (es decir, un 32% total).
            nota_base_inei = obtener_nota_inei(distrito)
            score_inei_ponderado = nota_base_inei * 0.32

            # Nota visual de seguridad (para mostrar al usuario del 0 al 10)
            # Reconstruimos la nota sobre 10 sumando las partes proporcionales
            nota_seguridad_visual = (obtener_nota_inei(distrito) * 0.8) + (mis_modulos.calcular_nota_seguridad(resultados_google['cantidades']['policia']) * 0.2)
            
            # 2. PRECIO (Vale 40%)
            nota_base_precio = calcular_nota_precio(precio)
            score_precio_ponderado = nota_base_precio * 0.40

            # --- C. SUMA FINAL (LA FÓRMULA MAESTRA) ---
            # 0.20 (Servicios) + 0.08 (Comisaría) + 0.32 (INEI) + 0.40 (Precio) = 1.00
            indice_final = score_servicios_ponderado + score_policia_ponderado + score_inei_ponderado + score_precio_ponderado

            # --- D. PREPARAR DATOS PARA EL HTML ---
            datos_resultado = round(indice_final, 2)
            
            # Guardamos las notas "sobre 10" para que el usuario las entienda
            notas_visuales = {
                "precio": round(nota_base_precio, 2),
                "seguridad": round(nota_seguridad_visual, 2),
                "servicios": round((score_servicios_ponderado / 0.2), 2) # Revertimos para mostrar sobre 10
            }
            
            detalles_api = resultados_google['cantidades']

    return render_template('index.html', 
                           puntaje_final=datos_resultado, 
                           notas=notas_visuales, 
                           detalles=detalles_api)

if __name__ == '__main__':
    app.run(debug=True)