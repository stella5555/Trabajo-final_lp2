import re

# Patrones principales encontrados en mbox-short.txt
regex_fechas = [
    # Formato 1: "Sat Jan  5 09:14:16 2008" (líneas From)
    r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+\d{4}\b',
    
    # Formato 2: "Date: Sat, 5 Jan 2008 09:14:16 -0500"
    r'Date:\s*(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*,?\s+\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\s+\d{2}:\d{2}:\d{2}\s+[+-]\d{4}',
    
    # Formato 3: "5 Jan 2008" (más simple)
    r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b',
    
    # Formato 4: "Jan 5, 2008" (alternativo)
    r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}\b',
    
    # Formato 5: Solo mes y día "Jan  5" (en líneas From)
    r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\b(?!:)'  # Excluye horas
]

# Versión más simple y efectiva para la mayoría de casos en mbox-short.txt
regex_simple = r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:,?\s+\d{4})?\b'