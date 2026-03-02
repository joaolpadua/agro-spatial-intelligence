from pathlib import Path
import geopandas as gpd
import matplotlib.pyplot as plt


def main():
    # =========================
    # Definição de caminhos
    # =========================
    base_dir = Path(__file__).resolve().parent.parent
    output_dir = base_dir / "outputs"

    print("Carregando base final com densidade...")
    gdf = gpd.read_file(output_dir / "soja_densidade_sp.geojson")

    # =========================
    # Configuração do mapa
    # =========================
    fig, ax = plt.subplots(figsize=(10, 12))

    # Plot com escala contínua
    gdf.plot(
        column="densidade_ton_km2",
        cmap="YlOrRd",  # Amarelo → Laranja → Vermelho
        linewidth=0.2,
        edgecolor="gray",
        legend=True,
        ax=ax
    )

    # =========================
    # Ajustes visuais
    # =========================
    ax.set_title(
        "Densidade Territorial de Produção de Soja (ton/km²)\nSão Paulo - 2021",
        fontsize=14
    )

    ax.axis("off")

    # =========================
    # Salvar mapa
    # =========================
    output_path = output_dir / "mapa_soja_densidade_sp.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")

    print("Mapa salvo em:", output_path)


if __name__ == "__main__":
    main()