from pathlib import Path
import geopandas as gpd
from pystac_client import Client
import planetary_computer as pc


def main():
    # =========================
    # Caminhos
    # =========================
    base_dir = Path(__file__).resolve().parent.parent
    municipios_path = base_dir / "outputs" / "soja_densidade_sp.geojson"

    print("Carregando municípios...")
    gdf = gpd.read_file(municipios_path)

    # Converter para WGS84 para consulta STAC
    gdf_wgs84 = gdf.to_crs(epsg=4326)

    bbox = gdf_wgs84.total_bounds

    print("Conectando ao STAC (Planetary Computer)...")
    catalog = Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")

    print("Buscando Sentinel-2 (2021-11 a 2022-03)...")

    search = catalog.search(
        collections=["sentinel-2-l2a"],
        bbox=bbox,
        datetime="2021-11-01/2022-03-31",
        query={"eo:cloud_cover": {"lt": 20}},
    )

    items = list(search.get_items())

    print(f"Cenas encontradas: {len(items)}")
    item = items[0]

    print("\nLink da banda B04 (Red):")
    print(item.assets["B04"].href)

    print("\nLink da banda B08 (NIR):")
    print(item.assets["B08"].href)

    print("\nID da cena:")
    print(item.id)

    print("\nData da cena:")
    print(item.datetime)

    print("\nCobertura de nuvem:")
    print(item.properties.get("eo:cloud_cover"))

    print("\nBBOX:")
    print(item.bbox)

    print("\nAssets disponíveis:")
    print(list(item.assets.keys()))


if __name__ == "__main__":
    main()