# scripts/__init__.py
"""
Lima Housing Analytics - Scripts Package
========================================

Módulos principales:
- scraper_urbania: Web scraping de Urbania.pe
- data_processor: Procesamiento y scoring de datos
- api_google: Integración con Google Maps API
- main: Script principal del pipeline
"""

__version__ = "1.0.0"
__author__ = "Chávez Mendoza Maria Fernanda y Cruz Cruz Hilary Penelope"

# Importaciones que estarán disponibles al hacer: from scripts import *
__all__ = [
    'scraper_urbania',
    'data_processor', 
    'api_google',
    'main'
]

# Inicialización del paquete
print(f"Lima Housing Analytics v{__version__} cargado")