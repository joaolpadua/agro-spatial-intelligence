from pathlib import Path
import geopandas as gpd
import pandas as pd
import numpy as np


def zscore(series):
    """
    Calcula z-score de uma série numérica.
    """
    return (series - series.mean()) / series.std()


def main():
    # =========================
    # Caminhos
    # =========================
    base_dir = Path(__file__).resolve().parent.parent
    input_path = base_dir / "outputs" / "soja_densidade_sp.geojson"
    output_dir = base_dir / "outputs"

    print("Carregando base consolidada do Projeto 01...")
    gdf = gpd.read_file(input_path)

    print(f"Municípios carregados: {len(gdf)}")

    # =========================
    # Placeholder para variáveis ambientais
    # =========================
    # Estas colunas serão preenchidas nos próximos scripts
    if "ndvi_medio" not in gdf.columns:
        gdf["ndvi_medio"] = np.nan

    if "altitude_media" not in gdf.columns:
        gdf["altitude_media"] = np.nan

    # =========================
    # Estrutura do índice
    # =========================
    print("Preparando estrutura do índice de potencial...")

    gdf["z_ndvi"] = np.nan
    gdf["z_altitude"] = np.nan
    gdf["potencial_score"] = np.nan

    # =========================
    # Salvar base estruturada
    # =========================
    output_geojson = output_dir / "indice_potencial_sp.geojson"
    output_csv = output_dir / "indice_potencial_sp.csv"

    gdf.to_file(output_geojson, driver="GeoJSON")
    gdf.drop(columns="geometry").to_csv(output_csv, index=False)

    print("Base de potencial criada.")
    print(f"Arquivos salvos em: {output_dir}")


if __name__ == "__main__":
    main()