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

    print("Carregando municípios...")
    gdf = gpd.read_file(municipios_path)

    # Selecionar município teste
    municipio = gdf[gdf["nome_municipio"] == "Salto Grande"]
    print("Município selecionado:", municipio["nome_municipio"].values[0])

    # STAC exige bbox em WGS84
    municipio_wgs84 = municipio.to_crs(epsg=4326)
    bbox = municipio_wgs84.total_bounds.tolist()

    print("BBOX em graus:", bbox)

    # =========================
    # Conectar ao STAC
    # =========================
    print("Conectando ao STAC (Planetary Computer)...")
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

    # Usar apenas 1 cena
    items = items[:1]
    item = items[0]

    # =========================
    # Empilhar bandas (CRS nativo)
    # =========================
    print("Empilhando bandas B04 e B08...")

    stack = stackstac.stack(
    items,
    assets=["B04", "B08"],
    resolution=10,
    epsg=32722
    )   

    print("CRS do raster:", stack.rio.crs)

    # Separar bandas
    red = stack.sel(band="B04")
    nir = stack.sel(band="B08")

    # Calcular NDVI
    ndvi = (nir - red) / (nir + red)
    print("NDVI calculado.")

    # Garantir CRS
    ndvi = ndvi.rio.write_crs(stack.rio.crs)

    # Reprojetar município para CRS do raster
    municipio_proj = municipio.to_crs(stack.rio.crs)

    # Recorte espacial
    ndvi_clip = ndvi.rio.clip(
        municipio_proj.geometry,
        municipio_proj.crs,
        drop=True
    )

    print("NDVI recortado.")

    # =========================
    # Plot
    # =========================
    plt.figure(figsize=(8, 6))
    ndvi_clip.isel(time=0).plot(cmap="RdYlGn")
    plt.title("NDVI - Salto Grande (Safra 2021/2022)")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()