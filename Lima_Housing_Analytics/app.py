from flask import Flask, render_template, request

# Aquí importarías tus módulos si los tienes listos
# import mis_modulos 
# import Google_places_api

app = Flask(__name__)

# --- RUTA PRINCIPAL ---
@app.route('/', methods=['GET', 'POST'])
def home():
    # Si el usuario llenó el formulario y dio clic en "Analizar":
    if request.method == 'POST':
        
        # 1. RECIBIMOS LOS DATOS (Sin pedir 'distrito' explícitamente)
        lugar = request.form.get('lugar', '')  # Ej: "Ceres, Ate"
        precio_str = request.form.get('precio', '0')
        precio = float(precio_str) if precio_str else 0.0

        # 2. EL TRUCO: Detectar el distrito automáticamente
        # Si el usuario escribió una coma (ej: "Plaza Vea, Ate")
        if "," in lugar:
            # Tomamos lo que está después de la coma
            distrito = lugar.split(',')[-1].strip().upper()
        else:
            # Si no puso coma, usamos un valor por defecto o lo que haya escrito
            distrito = "LIMA"

        print(f"✅ Datos recibidos -> Lugar: {lugar}, Distrito detectado: {distrito}, Precio: {precio}")

        # LEEMOS EL DATO REAL DEL FORMULARIO
        habitaciones = int(request.form.get('hab', 2)) 
        
        # Ahora la comparación es EXACTA
        nota_precio = mis_modulos.evaluar_precio_mercado(distrito, precio, habitaciones)

        # 3. AQUÍ VA TU LÓGICA DE CÁLCULO (Simulada para que no falle la demo)
        # Aquí deberías llamar a tus funciones: mis_modulos.calcular(...)
        # Por ahora pondremos datos fijos para que veas que la página FUNCIONA.
        
        puntaje_final = 8.5  # Ejemplo
        notas = {
            'seguridad': 16, 
            'precio': 14, 
            'servicios': 18
        }
        detalles = {
            'policia': 2  # Comisarías encontradas
        }

        # 4. Enviamos los resultados al HTML
        return render_template('index.html', 
                               puntaje_final=puntaje_final, 
                               notas=notas, 
                               detalles=detalles)

    # Si entra por primera vez (sin enviar datos)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)