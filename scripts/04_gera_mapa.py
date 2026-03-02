from pathlib import Path
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def plot_mapa_categorico(gdf, output_path):
    """
    Gera mapa categórico de densidade territorial de soja.
    Espera GeoDataFrame com coluna 'classe_densidade'.
    """

    fig, ax = plt.subplots(figsize=(10, 12))

    # Definição explícita de cores para controle visual executivo
    cores = {
        "Sem produção": "#f0f0f0",
        "Baixa": "#fdd49e",
        "Média": "#fc8d59",
        "Alta": "#d7301f"
    }

    gdf["cor"] = gdf["classe_densidade"].map(cores)

    gdf.plot(
        color=gdf["cor"],
        linewidth=0.2,
        edgecolor="gray",
        ax=ax
    )

    # Legenda construída manualmente para manter ordem e padronização
    handles = [
        mpatches.Patch(color=cores[k], label=k)
        for k in cores
    ]

    ax.legend(handles=handles, title="Classe de Densidade", loc="lower left")

    ax.set_title(
        "Densidade Territorial de Produção de Soja (ton/km²)\nSão Paulo - 2021"
    )

    ax.axis("off")

    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def main():
    base_dir = Path(__file__).resolve().parent.parent
    output_dir = base_dir / "outputs"

    print("Carregando base final...")
    gdf = gpd.read_file(output_dir / "soja_densidade_sp.geojson")

    output_path = output_dir / "mapa_soja_densidade_sp.png"

    plot_mapa_categorico(gdf, output_path)

    print("Mapa salvo em:", output_path)


if __name__ == "__main__":
    main()