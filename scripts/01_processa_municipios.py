from pathlib import Path
import geopandas as gpd


def main():
    # =========================
    # Caminhos
    # =========================
    base_dir = Path(__file__).resolve().parent.parent
    raw_dir = base_dir / "data" / "raw"
    processed_dir = base_dir / "data" / "processed"

    processed_dir.mkdir(exist_ok=True)

    # =========================
    # Carregar shapefile
    # =========================
    shp_files = list(raw_dir.glob("*.shp"))

    if not shp_files:
        raise FileNotFoundError("Nenhum shapefile encontrado em data/raw")

    shp_path = shp_files[0]
    print("Shapefile encontrado:", shp_path.name)

    gdf = gpd.read_file(shp_path)

    # =========================
    # Reprojetar
    # =========================
    gdf = gdf.to_crs(epsg=31983)

    # =========================
    # Calcular área
    # =========================
    gdf["area_km2"] = gdf.geometry.area / 1_000_000

    # =========================
    # Selecionar colunas essenciais
    # =========================
    gdf = gdf[["CD_MUN", "NM_MUN", "area_km2", "geometry"]]

    gdf = gdf.rename(columns={
        "CD_MUN": "codigo_ibge",
        "NM_MUN": "nome_municipio"
    })

    print("Municípios processados:", len(gdf))

    # =========================
    # Exportar GeoJSON
    # =========================
    output_path = processed_dir / "municipios_sp.geojson"
    gdf.to_file(output_path, driver="GeoJSON")

    print("Arquivo salvo em:", output_path)


if __name__ == "__main__":
    main()