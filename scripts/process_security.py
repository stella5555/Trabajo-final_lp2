import pandas as pd

# 1. Cargar CSV INEI
df = pd.read_csv("data/raw/security_raw.csv", encoding="latin1")

# 2. Filtrar SOLO Lima Metropolitana
df = df[df["DPTO_HECHO_NEW"].str.strip() == "LIMA METROPOLITANA"]

# 3. Filtrar SOLO provincia Lima
df = df[df["PROV_HECHO"].str.strip() == "LIMA"]

# 4. Limpiar distrito
df["district"] = (
    df["DIST_HECHO"]
    .astype(str)
    .str.upper()
    .str.strip()
)

# 5. Agrupar delitos por distrito
security = (
    df.groupby("district")["cantidad"]
    .sum()
    .reset_index()
)

security.rename(columns={"cantidad": "crime_count"}, inplace=True)


# Normalizar nombres de distrito (encoding + formato)
security["district"] = (
    security["district"]
    .str.upper()
    .str.replace("Ã", "Ñ")
    .str.strip()
)


max_crime = security["crime_count"].max()
min_crime = security["crime_count"].min()

security["security_score"] = (
    10 - (
        (security["crime_count"] - min_crime) /
        (max_crime - min_crime) * 10
    )
).round(2)


# 6. Guardar resultado
security.to_csv(
    "data/processed/security_by_district.csv",
    index=False,
    encoding="utf-8-sig"
)

print("✅ Seguridad INEI procesada correctamente")
print("📊 Distritos únicos:", security.shape[0])
print(security.sort_values("crime_count", ascending=False).head())
