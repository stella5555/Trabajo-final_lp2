import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

class UrbaniaScraper:
    def __init__(self):
        self.base_url = "https://urbania.pe"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    def scrape_district(self, district, operation="alquiler", max_pages=3):
        """Extrae propiedades de un distrito específico"""
        properties = []
        
        for page in range(1, max_pages + 1):
            url = f"{self.base_url}/buscar/{operation}-departamentos?districts={district}&page={page}"
            print(f"Scrapeando {district} - Página {page}: {url}")
            
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Buscar los contenedores de propiedades
                property_cards = soup.find_all('div', class_='card')
                
                if not property_cards:
                    print(f"No se encontraron propiedades en {district}, página {page}")
                    break
                
                for card in property_cards:
                    property_data = self.extract_property_data(card)
                    if property_data:
                        property_data['district'] = district
                        property_data['operation'] = operation
                        properties.append(property_data)
                
                time.sleep(2)  # Espera para no sobrecargar el servidor
                
            except Exception as e:
                print(f"Error en {district}, página {page}: {e}")
                continue
        
        return properties
    
    def extract_property_data(self, card):
        """Extrae datos específicos de una propiedad"""
        try:
            # Título y link
            title_elem = card.find('a', class_='title')
            title = title_elem.text.strip() if title_elem else "No disponible"
            link = title_elem['href'] if title_elem else ""
            
            # Precio
            price_elem = card.find('div', class_='price')
            price = price_elem.text.strip() if price_elem else "0"
            
            # Dirección
            address_elem = card.find('div', class_='address')
            address = address_elem.text.strip() if address_elem else ""
            
            # Características (m², habitaciones, baños)
            features = card.find_all('div', class_='feature')
            area = "0"
            bedrooms = "0"
            bathrooms = "0"
            
            for feature in features:
                text = feature.text.strip().lower()
                if 'm²' in text:
                    area = text.replace('m²', '').strip()
                elif 'dorm' in text or 'hab' in text:
                    bedrooms = text.split()[0]
                elif 'baño' in text:
                    bathrooms = text.split()[0]
            
            return {
                'title': title,
                'price': self.clean_price(price),
                'area': self.clean_number(area),
                'bedrooms': self.clean_number(bedrooms),
                'bathrooms': self.clean_number(bathrooms),
                'address': address,
                'link': f"{self.base_url}{link}" if link else "",
                'scraped_date': pd.Timestamp.now().strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            print(f"Error extrayendo datos de propiedad: {e}")
            return None
    
    def clean_price(self, price_text):
        """Limpia el texto de precio y convierte a número"""
        try:
            # Eliminar símbolos y texto
            clean = price_text.replace('S/', '').replace(',', '').replace(' ', '')
            # Tomar solo números
            numbers = ''.join(filter(str.isdigit, clean))
            return float(numbers) if numbers else 0
        except:
            return 0
    
    def clean_number(self, text):
        """Limpia números de características"""
        try:
            numbers = ''.join(filter(str.isdigit, text))
            return float(numbers) if numbers else 0
        except:
            return 0
    
    def save_to_csv(self, properties, filename="urbania_properties.csv"):
        """Guarda los datos en CSV"""
        if not properties:
            print("No hay propiedades para guardar")
            return
        
        df = pd.DataFrame(properties)
        
        # Crear carpeta data/raw si no existe
        os.makedirs('data/raw', exist_ok=True)
        
        filepath = f"data/raw/{filename}"
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"Datos guardados en {filepath} ({len(df)} propiedades)")
        
        return df

def main():
    scraper = UrbaniaScraper()
    
    # Distritos de Lima a scrapear (puedes agregar más)
    districts = [
        "miraflores",
        "surco",
        "san-isidro",
        "barranco",
        "la-molina",
        "jesus-maria",
        "lince",
        "san-miguel",
        "magdalena",
        "pueblo-libre"
    ]
    
    all_properties = []
    
    for district in districts:
        print(f"\n{'='*50}")
        print(f"Scrapeando: {district}")
        print('='*50)
        
        properties = scraper.scraper_district(district, max_pages=2)
        all_properties.extend(properties)
        
        print(f"Encontradas: {len(properties)} propiedades")
        time.sleep(3)  # Pausa entre distritos
    
    # Guardar todos los datos
    if all_properties:
        scraper.save_to_csv(all_properties, "urbania_lima_alquileres.csv")
        
        # Mostrar resumen
        df = pd.DataFrame(all_properties)
        print(f"\n{'='*50}")
        print("RESUMEN DEL SCRAPING")
        print('='*50)
        print(f"Total propiedades: {len(df)}")
        print(f"Distritos cubiertos: {df['district'].nunique()}")
        print(f"Precio promedio: S/ {df['price'].mean():,.0f}")
        print(f"Área promedio: {df['area'].mean():,.0f} m²")
        print(f"\nDistritos scrapeados: {', '.join(df['district'].unique())}")
    else:
        print("No se encontraron propiedades")

if __name__ == "__main__":
    main()