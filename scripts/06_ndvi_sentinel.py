from pathlib import Path
import geopandas as gpd
from pystac_client import Client
import planetary_computer as pc
import stackstac
import rioxarray
import matplotlib.pyplot as plt


def main():

    # =========================
    # Caminhos
    # =========================
    base_dir = Path(__file__).resolve().parent.parent
    municipios_path = base_dir / "outputs" / "soja_densidade_sp.geojson"
    output_dir = base_dir / "outputs"

    print("Carregando municípios...")
    gdf = gpd.read_file(municipios_path)

    municipio = gdf[gdf["nome_municipio"] == "Salto Grande"]

    if municipio.empty:
        print("Município não encontrado.")
        return

    print("Município selecionado:", municipio["nome_municipio"].values[0])

    # STAC exige bbox em WGS84
    municipio_wgs84 = municipio.to_crs(epsg=4326)
    bbox = municipio_wgs84.total_bounds.tolist()

    print("BBOX em graus:", bbox)

    # =========================
    # STAC
    # =========================
    print("Conectando ao STAC...")
    catalog = Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=pc.sign_inplace
    )

    print("Buscando Sentinel-2...")
    search = catalog.search(
        collections=["sentinel-2-l2a"],
        bbox=bbox,
        datetime="2021-11-01/2022-03-31",
        query={"eo:cloud_cover": {"lt": 20}},
    )

    items = list(search.items())
    print("Cenas encontradas:", len(items))

    if not items:
        print("Nenhuma cena encontrada.")
        return

    items = items[:1]

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

    print("CRS do raster:", stack.rio.crs)

    red = stack.sel(band="B04")
    nir = stack.sel(band="B08")

    ndvi = (nir - red) / (nir + red)
    ndvi = ndvi.rio.write_crs(stack.rio.crs)

    municipio_proj = municipio.to_crs(stack.rio.crs)

    ndvi_clip = ndvi.rio.clip(
        municipio_proj.geometry,
        municipio_proj.crs,
        drop=True
    )

    print("NDVI calculado e recortado.")

    # =========================
    # Estatísticas espaciais
    # =========================
    print("\nCalculando estatísticas...")

    ndvi_medio = (
        ndvi_clip.mean(dim=("y", "x")).compute().item()
    )

    ndvi_mediana = (
        ndvi_clip.median(dim=("y", "x")).compute().item()
    )

    ndvi_std = (
        ndvi_clip.std(dim=("y", "x")).compute().item()
    )

    print(f"NDVI médio: {ndvi_medio:.4f}")
    print(f"NDVI mediana: {ndvi_mediana:.4f}")
    print(f"Desvio padrão: {ndvi_std:.4f}")

    # =========================
    # Salvar mapa automaticamente
    # =========================
    fig, ax = plt.subplots(figsize=(8, 6))
    ndvi_clip.isel(time=0).plot(cmap="RdYlGn", ax=ax)
    ax.set_title("NDVI - Salto Grande (Safra 2021/2022)")
    ax.axis("off")

    output_path = output_dir / "ndvi_salto_grande.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"Mapa salvo em: {output_path}")


if __name__ == "__main__":
    main()