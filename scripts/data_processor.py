import pandas as pd
import os

def calculate_scores(df):
    """Aplica la fórmula de scoring del proyecto"""
    # Tu fórmula: (Costo*0.4 + Seguridad*0.4 + Servicios*0.2)
    df['final_score'] = (
        df['cost_score'] * 0.4 + 
        df['safety_score'] * 0.4 + 
        df['services_score'] * 0.2
    )
    df['final_score'] = df['final_score'].round(1)
    return df.sort_values('final_score', ascending=False)

def main():
    print("📊 PROCESANDO DATOS PARA SCORING...")
    
    # Cargar datos
    df = pd.read_csv('data/processed/dataset_final.csv')
    
    # Calcular scores
    df_scored = calculate_scores(df)
    
    # Guardar
    output_path = 'data/processed/scored_properties.csv'
    df_scored.to_csv(output_path, index=False)
    
    print(f"✅ Scores calculados para {len(df)} propiedades")
    print(f"🏆 Top 5 propiedades:")
    print(df_scored[['district', 'price_soles', 'final_score']].head())
    
    return df_scored

if __name__ == "__main__":
    main()