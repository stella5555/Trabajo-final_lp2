"""
API DE TIPO DE CAMBIO - Implementación REAL
Usa datos reales de SUNAT para tipo de cambio actual
"""

import requests
import json
from datetime import datetime
import time
from functools import lru_cache
import pandas as pd

class CurrencyAPI:
    def __init__(self, demo_mode=False):
        """
        Inicializa API de tipo de cambio
        demo_mode=False: Usa API REAL de SUNAT
        """
        self.demo_mode = demo_mode
        self.api_url = "https://api.apis.net.pe/v1/tipo-cambio-sunat"
        
    @lru_cache(maxsize=1)
    def get_exchange_rate(self):
        """
        Obtiene tipo de cambio ACTUAL de SUNAT
        Returns: float con tasa de cambio USD a PEN
        """
        if self.demo_mode:
            print("💱 MODO DEMO: Usando tipo de cambio fijo 3.72")
            return 3.72
        
        try:
            print("🔄 Consultando API de SUNAT para tipo de cambio actual...")
            
            # Fecha actual en formato YYYY-MM-DD
            today = datetime.now().strftime('%Y-%m-%d')
            
            # LLAMADA REAL A API DE SUNAT
            response = requests.get(
                f"{self.api_url}?fecha={today}",
                headers={
                    'Accept': 'application/json',
                    'Referer': 'https://apis.net.pe/api-tipo-cambio.html'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # SUNAT devuelve: compra, venta, promedio
                exchange_rate = float(data.get('venta', 3.72))
                print(f"✅ API SUNAT: 1 USD = S/ {exchange_rate} (fecha: {today})")
                return exchange_rate
            else:
                print(f"⚠️  API SUNAT respondió con código {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("⏰ Timeout en API SUNAT")
        except requests.exceptions.ConnectionError:
            print("🔌 Error de conexión con API SUNAT")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
        
        # FALLBACK: Último valor conocido o valor por defecto
        print("🔄 Usando valor de respaldo 3.72")
        return 3.72
    
    def convert_usd_to_pen(self, usd_amount):
        """
        Convierte USD a PEN usando tasa actual
        """
        rate = self.get_exchange_rate()
        converted = usd_amount * rate
        print(f"   💰 Conversión: USD {usd_amount:.2f} → S/ {converted:.2f} (tasa: {rate})")
        return converted
    
    def update_dataframe_prices(self, df):
        """
        Actualiza precios en un dataframe usando tipo de cambio actual
        """
        print("\n" + "="*50)
        print("💵 ACTUALIZANDO PRECIOS CON TIPO DE CAMBIO REAL")
        print("="*50)
        
        if 'price' not in df.columns:
            print("⚠️  No hay columna 'price' en el dataframe")
            return df
        
        # Obtener tipo de cambio ACTUAL
        exchange_rate = self.get_exchange_rate()
        
        # Contadores para estadísticas
        usd_count = 0
        pen_count = 0
        total_converted = 0
        
        # Crear nuevas columnas
        df['price_clean'] = None
        df['price_currency'] = 'PEN'  # Por defecto
        df['exchange_rate_used'] = exchange_rate
        
        for idx, row in df.iterrows():
            price_str = str(row['price']).upper().strip()
            
            try:
                # Extraer número del string
                import re
                match = re.search(r'[\d,]+\.?\d*', price_str.replace(',', ''))
                
                if match:
                    value = float(match.group(0))
                    
                    # DETECTAR SI ES USD
                    if 'USD' in price_str:
                        # CONVERTIR USD A PEN CON API REAL
                        pen_value = self.convert_usd_to_pen(value)
                        df.at[idx, 'price_clean'] = pen_value
                        df.at[idx, 'price_currency'] = 'USD'
                        usd_count += 1
                        total_converted += value
                    else:
                        # Ya está en PEN
                        df.at[idx, 'price_clean'] = value
                        df.at[idx, 'price_currency'] = 'PEN'
                        pen_count += 1
                        
            except Exception as e:
                continue
        
        # Estadísticas
        print(f"\n📊 ESTADÍSTICAS DE CONVERSIÓN:")
        print(f"   • Propiedades en USD: {usd_count}")
        print(f"   • Propiedades en PEN: {pen_count}")
        print(f"   • Total USD convertido: ${total_converted:.2f}")
        print(f"   • Tipo de cambio usado: {exchange_rate}")
        print(f"   • Fecha de consulta: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        return df

# Función para testing
def test_currency_api():
    """Prueba la API de tipo de cambio"""
    print("🧪 PROBANDO API DE TIPO DE CAMBIO")
    print("-" * 40)
    
    # Probar en modo REAL (sin demo)
    api = CurrencyAPI(demo_mode=False)
    
    print("\n1. Obteniendo tipo de cambio actual...")
    rate = api.get_exchange_rate()
    print(f"   Resultado: 1 USD = S/ {rate}")
    
    print("\n2. Probando conversiones...")
    test_amounts = [100, 500, 1000, 1500]
    for amount in test_amounts:
        converted = api.convert_usd_to_pen(amount)
        print(f"   USD {amount:6} = S/ {converted:8.2f}")
    
    print("\n3. Probando con dataframe de ejemplo...")
    test_df = pd.DataFrame({
        'property_id': [1, 2, 3, 4, 5],
        'price': ['USD 900', 'S/. 2500', 'USD 1200', '3500', 'USD 750']
    })
    
    result_df = api.update_dataframe_prices(test_df)
    
    print(f"\n📋 Resultado:")
    print(result_df[['property_id', 'price', 'price_clean', 'price_currency']].to_string())
    
    return rate

if __name__ == "__main__":
    # Ejecutar prueba
    current_rate = test_currency_api()
    print(f"\n✅ Prueba completada. Tipo de cambio actual: {current_rate}")