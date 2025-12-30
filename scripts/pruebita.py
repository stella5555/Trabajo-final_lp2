import json

# Cargar el JSON
with open('web/data/properties.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extraer distritos únicos
distritos = sorted(set([p['district'] for p in data if p.get('district')]))

print(f"📊 Total de distritos únicos: {len(distritos)}")
print("\n🏙️ LISTA DE DISTRITOS:")
print("=" * 40)

# Mostrar en columnas
for i, distrito in enumerate(distritos, 1):
    # Contar propiedades por distrito
    count = sum(1 for p in data if p.get('district') == distrito)
    print(f"{i:2d}. {distrito:25s} ({count:3d} propiedades)")

# Estadísticas
print(f"\n📈 ESTADÍSTICAS:")
print(f"• Distritos únicos: {len(distritos)}")
print(f"• Total propiedades: {len(data)}")

# Top 10 distritos con más propiedades
from collections import Counter
distrito_counts = Counter([p['district'] for p in data if p.get('district')])
top_10 = distrito_counts.most_common(10)

print(f"\n🏆 TOP 10 DISTRITOS CON MÁS PROPIEDADES:")
for distrito, count in top_10:
    print(f"  • {distrito}: {count} propiedades")