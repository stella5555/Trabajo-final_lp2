# organize_project.py CORREGIDO
import os
import shutil

def organize_project():
    """Organiza todos los archivos del proyecto"""
    print("📁 ORGANIZANDO PROYECTO FINAL")
    print("="*50)
    
    # 1. Crear estructura de carpetas
    folders = [
        'web/assets/img',
        'web/css',
        'web/js',
        'data/raw',
        'data/processed',
        'scripts'
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✅ Carpeta creada: {folder}")
    
    # 2. Mover capturas de pantalla a assets
    screenshots = ['debug_urbania_loaded.png', 'debug_urbania.png']
    for screenshot in screenshots:
        if os.path.exists(screenshot):
            try:
                shutil.move(screenshot, f'web/assets/img/{screenshot}')
                print(f"📸 Movida: {screenshot} → web/assets/img/")
            except Exception as e:
                print(f"⚠️  No se pudo mover {screenshot}: {e}")
    
    # 3. Verificar archivos críticos
    critical_files = {
        'scripts/scraper_urbania.py': 'Scraper principal',
        'scripts/create_sample_data.py': 'Generador de dataset',
        'scripts/data_processor.py': 'Fórmula de scoring',
        'data/raw/urbania_properties.csv': '6 propiedades REALES',
        'data/processed/combined_dataset.csv': 'Dataset combinado',
        'debug_urbania_loaded.png': 'Captura de Cloudflare'
    }
    
    print("\n🔍 VERIFICANDO ARCHIVOS CRÍTICOS:")
    print("-"*40)
    
    all_ok = True
    for file, description in critical_files.items():
        if os.path.exists(file):
            print(f"✅ {file:45} - {description}")
        else:
            print(f"❌ {file:45} - FALTANTE: {description}")
            all_ok = False
    
    # 4. Crear README simplificado
    if not os.path.exists('README.md'):
        readme_content = """# 🏡 Lima Housing Analytics

## 📊 Proyecto Final LP2 - Análisis de Precios Inmobiliarios vs. Calidad de Vida

**Integrantes:**
- Chávez Mendoza Maria Fernanda
- Cruz Cruz Hilary Penelope

## 🎯 Objetivo
Democratizar la calidad de vida en Lima identificando zonas con mejor relación costo-beneficio.

## 🛡️ Desafío Técnico
Urbania.pe utiliza Cloudflare para protección anti-bot.

**Solución:** Dataset sintético realista + 6 propiedades reales extraídas.

## 📁 Estructura