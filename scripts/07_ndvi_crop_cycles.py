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


# ==========================================================
# Salvar snapshot NDVI de uma data específica
# ==========================================================
def salvar_ndvi_snapshot(ndvi_clip, date, path):

    # selecionar cena
    scene = ndvi_clip.sel(time=date)

    # converter para numpy
    arr = scene.values

    # remover dimensões extras automaticamente
    while arr.ndim > 2:
        arr = arr[0]

    fig, ax = plt.subplots(figsize=(5,5))

    im = ax.imshow(
        arr,
        cmap="YlGn",
        vmin=0,
        vmax=1
    )

    plt.colorbar(im, ax=ax)

    ax.set_title(str(date.date()))
    ax.axis("off")

    plt.tight_layout()
    plt.savefig(path, dpi=200)
    plt.close()

def main():

    # ==========================================================
    # Caminhos do projeto
    # ==========================================================
    base_dir = Path(__file__).resolve().parent.parent

    kml_path = base_dir / "input" / "lucas_ag_area.kml"
    output_dir = base_dir / "outputs"

    peaks_dir = output_dir / "peaks"
    valleys_dir = output_dir / "valleys"

    peaks_dir.mkdir(exist_ok=True)
    valleys_dir.mkdir(exist_ok=True)

    # ==========================================================
    # Carregar área do KML
    # ==========================================================
    print("Carregando área do KML...")
    area = gpd.read_file(kml_path)

    # STAC trabalha em WGS84
    area_wgs84 = area.to_crs(epsg=4326)

    # ==========================================================
    # Detectar automaticamente zona UTM
    # ==========================================================
    centroid = area_wgs84.geometry.union_all().centroid

    lon = centroid.x
    lat = centroid.y

    zone = int((lon + 180) / 6) + 1

    if lat >= 0:
        epsg_utm = 32600 + zone
    else:
        epsg_utm = 32700 + zone

    print(f"UTM detectado automaticamente: EPSG:{epsg_utm}")

    bbox = area_wgs84.total_bounds.tolist()
    print("BBOX da área:", bbox)

    # ==========================================================
    # Conectar ao Planetary Computer
    # ==========================================================
    print("Conectando ao Planetary Computer...")

    catalog = Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=pc.sign_inplace
    )

    # ==========================================================
    # Buscar Sentinel-2
    # ==========================================================
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

    # ==========================================================
    # Empilhar imagens Sentinel
    # ==========================================================
    print("Empilhando bandas...")

    stack = stackstac.stack(
        items,
        assets=["B04", "B08"],
        resolution=10,
        epsg=epsg_utm
    )

    red = stack.sel(band="B04")
    nir = stack.sel(band="B08")

    # NDVI
    ndvi = (nir - red) / (nir + red)

    ndvi = ndvi.rio.write_crs(stack.rio.crs)

    # ==========================================================
    # Recorte espacial pelo polígono
    # ==========================================================
    area_proj = area.to_crs(epsg_utm)

    ndvi_clip = ndvi.rio.clip(
        area_proj.geometry,
        area_proj.crs,
        drop=True
    )

    print("NDVI calculado e recortado.")

    # ==========================================================
    # Série temporal NDVI médio
    # ==========================================================
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

    # metadados temporais úteis
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month

    # ==========================================================
    # Suavização da curva NDVI
    # ==========================================================
    df["ndvi_smooth"] = df["ndvi"].rolling(
        window=5,
        center=True
    ).mean()

    # ==========================================================
    # Detectar picos e vales
    # ==========================================================
    print("Detectando picos de vegetação...")

    peaks, _ = find_peaks(
        df["ndvi_smooth"].fillna(0),
        height=0.5,
        distance=10
    )

    valleys, _ = find_peaks(
        -df["ndvi_smooth"].fillna(0),
        distance=10
    )

    df["peak"] = False
    df.loc[peaks, "peak"] = True

    df["valley"] = False
    df.loc[valleys, "valley"] = True

    print("Picos detectados:", len(peaks))
    print("Vales detectados:", len(valleys))

    # ==========================================================
    # Salvar CSV
    # ==========================================================
    csv_path = output_dir / "ndvi_timeseries_lucas.csv"
    df.to_csv(csv_path, index=False)

    print("CSV salvo:", csv_path)

    # ==========================================================
    # Salvar snapshots NDVI
    # ==========================================================
    print("Salvando snapshots de picos...")

    for i in peaks:

        date = dates[i]
        filename = f"peak_{date.date()}.png"
        path = peaks_dir / filename

        salvar_ndvi_snapshot(ndvi_clip, date, path)

    print("Salvando snapshots de vales...")

    for i in valleys:

        date = dates[i]
        filename = f"valley_{date.date()}.png"
        path = valleys_dir / filename

        salvar_ndvi_snapshot(ndvi_clip, date, path)

    # ==========================================================
    # Plot da série temporal
    # ==========================================================
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