# scraper_urbania_stealth.py
import time
import pandas as pd
from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import re
import os

class UrbaniaStealthScraper:
    def __init__(self, headless=False):
        print("🕵️  INICIANDO SCRAPER STEALTH (Anti-detection)")
        
        # 1. CONFIGURACIÓN AVANZADA DE CHROME
        options = webdriver.ChromeOptions()
        
        if not headless:  # SIEMPRE visible para debugging
            options.add_argument("start-maximized")
        
        # Opciones críticas para evitar detección
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Más opciones para parecer humano
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        
        # User-Agent personalizado (Windows 10, Chrome real)
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # 2. INICIAR DRIVER
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        # 3. APLICAR STEALTH (ANTES DE CUALQUIER NAVEGACIÓN)
        stealth(self.driver,
                languages=["es-ES", "es", "en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )
        
        self.wait = WebDriverWait(self.driver, 20)  # Wait más largo
        self.properties_data = []
        
    def navigate_safely(self, url):
        """Navegación segura con múltiples verificaciones"""
        print(f"\n🌐 Navegando a: {url}")
        
        try:
            self.driver.get(url)
            
            # Espera inicial CRÍTICA
            time.sleep(5)
            
            # DEBUG: Guardar captura
            self.driver.save_screenshot("debug_urbania_loaded.png")
            print("📸 Captura guardada: debug_urbania_loaded.png")
            
            # Verificar si cargó contenido real
            page_source = self.driver.page_source.lower()
            
            # Señales de bloqueo
            block_signals = ["access denied", "cloudflare", "captcha", "robot", "verification"]
            for signal in block_signals:
                if signal in page_source:
                    print(f"⚠️  POSIBLE BLOQUEO detectado: '{signal}'")
                    return False
            
            # Señales de éxito
            success_signals = ["departamento", "alquiler", "propiedad", "inmueble", "precio"]
            success_count = sum(1 for signal in success_signals if signal in page_source)
            
            if success_count >= 2:
                print(f"✅ Página cargada correctamente ({success_count} señales de éxito)")
                return True
            else:
                print("❌ Página cargó pero sin contenido esperado")
                return False
                
        except Exception as e:
            print(f"❌ Error navegando: {e}")
            return False
    
    def extract_with_patience(self, district):
        """Extrae propiedades con mucha paciencia"""
        print(f"\n🔍 BUSCANDO EN: {district.upper()}")
        
        # URL específica (probemos diferentes formatos)
        url_variants = [
            f"https://urbania.pe/alquiler-de-departamentos-en-{district}",
            f"https://urbania.pe/buscar/alquiler-departamentos?districts={district}",
            f"https://urbania.pe/buscar/alquiler?districts={district}"
        ]
        
        for url in url_variants:
            print(f"  Probando URL: {url}")
            if self.navigate_safely(url):
                break
            time.sleep(3)
        
        # ESPERA INTELIGENTE para contenido dinámico
        print("⏳ Esperando contenido dinámico...")
        
        # Intentar diferentes selectores
        selectors_to_try = [
            "div[class*='posting']",
            "article[data-qa*='posting']", 
            "div[data-testid*='posting']",
            ".posting-card",
            ".property-card",
            "div.card"
        ]
        
        for selector in selectors_to_try:
            try:
                print(f"  Buscando con selector: {selector}")
                elements = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                )
                
                if elements and len(elements) > 3:
                    print(f"✅ Encontrados {len(elements)} elementos con: {selector}")
                    return self.process_elements(elements, district)
                    
            except Exception as e:
                print(f"  Selector falló: {selector}")
                continue
        
        print("❌ No se encontraron propiedades con ningún selector")
        return 0
    
    def process_elements(self, elements, district):
        """Procesa los elementos encontrados"""
        print(f"📊 Procesando {len(elements)} elementos...")
        
        count = 0
        for i, element in enumerate(elements[:30]):  # Limitar a 30
            try:
                # Scroll suave a cada elemento
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                time.sleep(0.1)
                
                data = self.extract_data_smart(element, district)
                if data:
                    self.properties_data.append(data)
                    count += 1
                    
                    if count % 5 == 0:
                        print(f"  ✅ {count} propiedades extraídas")
                        
            except Exception as e:
                if i < 5:  # Solo mostrar primeros errores
                    print(f"  ⚠️  Error elemento {i}: {str(e)[:40]}")
        
        return count
    
    def extract_data_smart(self, element, district):
        """Extrae datos de forma inteligente"""
        try:
            text = element.text
            
            # Extraer precio (con múltiples patrones)
            price = 0
            price_match = re.search(r'S/\s*([\d,]+)', text)
            if price_match:
                try:
                    price = float(price_match.group(1).replace(',', ''))
                except:
                    pass
            
            # Solo si tiene precio realista
            if not (500 < price < 50000):
                return None
            
            # Extraer área
            area = 0
            area_match = re.search(r'(\d+)\s*(?:m²|m2|m\s*²)', text)
            if area_match:
                area = float(area_match.group(1))
            
            # Extraer habitaciones
            bedrooms = 0
            bed_match = re.search(r'(\d+)\s*(?:dorm|hab)', text, re.IGNORECASE)
            if bed_match:
                bedrooms = int(bed_match.group(1))
            
            # Título (primera línea no vacía)
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            title = lines[0][:80] if lines else f"Propiedad en {district}"
            
            return {
                'title': title,
                'price': price,
                'area': area,
                'bedrooms': bedrooms,
                'district': district.capitalize(),
                'scraped_date': pd.Timestamp.now().strftime('%Y-%m-%d'),
                'source': 'urbania_stealth'
            }
            
        except Exception as e:
            return None
    
    def save_results(self):
        """Guarda los resultados"""
        if not self.properties_data:
            print("\n❌ No hay datos para guardar")
            return None
        
        df = pd.DataFrame(self.properties_data)
        
        # Filtrar
        df = df[df['price'] > 0]
        
        os.makedirs('data/raw', exist_ok=True)
        filename = f"data/raw/urbania_stealth_{pd.Timestamp.now().strftime('%Y%m%d')}.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        print(f"\n💾 RESULTADOS:")
        print(f"  Archivo: {filename}")
        print(f"  Propiedades: {len(df)}")
        
        if not df.empty:
            print(f"  Precio promedio: S/ {df['price'].mean():,.0f}")
            print(f"  Distritos únicos: {', '.join(df['district'].unique())}")
        
        return df
    
    def close(self):
        self.driver.quit()
        print("\n👋 Navegador cerrado")

def main():
    print("="*70)
    print("🏠 URBANIA SCRAPER CON STEALTH TECHNOLOGY")
    print("="*70)
    print("⚠️  ADVERTENCIA: Este script intenta evitar sistemas anti-bot")
    print("   Urbania puede bloquear IPs con uso intensivo")
    print("   Usa con moderación y fines educativos")
    print("="*70)
    
    scraper = UrbaniaStealthScraper(headless=False)
    
    try:
        # SOLO 2 distritos para prueba
        districts = ['miraflores', 'surco']
        
        total = 0
        for district in districts:
            count = scraper.extract_with_patience(district)
            total += count
            
            if count == 0:
                print(f"⚠️  No se pudo extraer de {district}, saltando...")
            
            # Pausa larga entre distritos
            if district != districts[-1]:
                print(f"\n⏳ Pausa de 10 segundos...")
                time.sleep(10)
        
        print(f"\n{'='*70}")
        print(f"📊 TOTAL: {total} propiedades extraídas")
        
        if total > 0:
            df = scraper.save_results()
            if df is not None:
                print(f"\n🎯 MUESTRA DE DATOS:")
                print(df[['district', 'price', 'area', 'bedrooms']].head().to_string())
        else:
            print("❌ No se extrajo ninguna propiedad")
            print("\n💡 RECOMENDACIÓN: Usa datos de muestra y continúa con las APIs")
            
    except KeyboardInterrupt:
        print("\n⚠️  Interrumpido por usuario")
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
    finally:
        scraper.close()
    
    return total > 0

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n" + "="*70)
        print("🔥 ALTERNATIVA RÁPIDA:")
        print("="*70)
        print("Si Urbania bloquea persistentemente, te recomiendo:")
        print("1. Usar datos de muestra realistas que ya tenemos")
        print("2. Continuar con APIs de Google Maps y dashboard")
        print("3. El scraper puede ser proyecto aparte")
        print("\n¿Quieres que te ayude con los datos de muestra?")