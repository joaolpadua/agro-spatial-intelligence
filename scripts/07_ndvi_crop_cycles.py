from pathlib import Path
import geopandas as gpd
import pandas as pd
import numpy as np

from pystac_client import Client
import planetary_computer as pc
import stackstac
import rioxarray

import matplotlib.pyplot as plt
from scipy.signal import find_peaks


def main():

    # =========================
    # Caminhos
    # =========================
    base_dir = Path(__file__).resolve().parent.parent

    kml_path = base_dir / "input" / "lucas_ag_area.kml"
    output_dir = base_dir / "outputs"

    print("Carregando área do KML...")
    area = gpd.read_file(kml_path)

    # Sentinel STAC usa WGS84
    area_wgs84 = area.to_crs(epsg=4326)

    bbox = area_wgs84.total_bounds.tolist()

    print("BBOX da área:", bbox)

    # =========================
    # Conectar ao STAC
    # =========================
    print("Conectando ao Planetary Computer...")

    catalog = Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=pc.sign_inplace
    )

    # =========================
    # Buscar Sentinel
    # =========================
    print("Buscando Sentinel-2...")

    search = catalog.search(
        collections=["sentinel-2-l2a"],
        bbox=bbox,
        datetime="2019-01-01/2024-12-31",
        query={"eo:cloud_cover": {"lt": 20}}
    )

    items = list(search.items())

    print("Cenas encontradas:", len(items))

    if len(items) == 0:
        print("Nenhuma cena encontrada.")
        return

    # =========================
    # Stack raster
    # =========================
    print("Empilhando bandas...")

    stack = stackstac.stack(
        items,
        assets=["B04", "B08"],
        resolution=10,
        epsg=32722
    )

    red = stack.sel(band="B04")
    nir = stack.sel(band="B08")

    ndvi = (nir - red) / (nir + red)

    ndvi = ndvi.rio.write_crs(stack.rio.crs)

    # =========================
    # Recorte espacial
    # =========================
    area_proj = area.to_crs(stack.rio.crs)

    ndvi_clip = ndvi.rio.clip(
        area_proj.geometry,
        area_proj.crs,
        drop=True
    )

    print("NDVI calculado e recortado.")

    # =========================
    # Série temporal
    # =========================
    print("Calculando NDVI médio por data...")

    ndvi_mean = (
        ndvi_clip
        .mean(dim=("y", "x"))
        .compute()
    )

    dates = pd.to_datetime(ndvi_mean["time"].values)
    values = ndvi_mean.values

    df = pd.DataFrame({
        "date": dates,
        "ndvi": values
    })

    df = df.sort_values("date")

    # =========================
    # Suavização
    # =========================
    df["ndvi_smooth"] = df["ndvi"].rolling(
        window=5,
        center=True
    ).mean()

    # =========================
    # Detectar picos
    # =========================
    print("Detectando picos de vegetação...")

    peaks, _ = find_peaks(
        df["ndvi_smooth"].fillna(0),
        height=0.5,
        distance=10
    )

    df["peak"] = False
    df.loc[peaks, "peak"] = True

    print("Picos detectados:", len(peaks))

    # =========================
    # Salvar CSV
    # =========================
    csv_path = output_dir / "ndvi_timeseries_lucas.csv"

    df.to_csv(csv_path, index=False)

    print("CSV salvo:", csv_path)

    # =========================
    # Plot
    # =========================
    fig, ax = plt.subplots(figsize=(10,5))

    ax.plot(df["date"], df["ndvi"], alpha=0.4, label="NDVI")
    ax.plot(df["date"], df["ndvi_smooth"], label="NDVI suavizado")

    ax.scatter(
        df.loc[df["peak"], "date"],
        df.loc[df["peak"], "ndvi_smooth"],
        color="red",
        label="picos de safra"
    )

    ax.set_title("Detecção de ciclos agrícolas - Lucas do Rio Verde")
    ax.set_ylabel("NDVI")
    ax.set_xlabel("Ano")

    ax.legend()

    plt.tight_layout()

    fig_path = output_dir / "ndvi_crop_cycles_lucas.png"

    plt.savefig(fig_path, dpi=300)

    plt.close()

    print("Gráfico salvo:", fig_path)

    print("\nProcesso concluído.")


if __name__ == "__main__":
    main()