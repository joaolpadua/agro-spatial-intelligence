from pathlib import Path
import geopandas as gpd
import pandas as pd


def main():
    # =========================
    # Definição de caminhos
    # =========================
    base_dir = Path(__file__).resolve().parent.parent
    processed_dir = base_dir / "data" / "processed"
    output_dir = base_dir / "outputs"
    output_dir.mkdir(exist_ok=True)

    # =========================
    # Carregar base territorial (GeoDataFrame)
    # =========================
    print("Carregando base territorial...")
    municipios = gpd.read_file(processed_dir / "municipios_sp.geojson")

    # =========================
    # Carregar base de produção (DataFrame)
    # =========================
    print("Carregando produção de soja...")
    soja = pd.read_csv(processed_dir / "soja_sp_2021.csv")

    # Remover sufixo " - SP" do nome (padronização estética; merge é por código)
    soja["nome_municipio"] = soja["nome_municipio"].str.replace(r"\s*-\s*SP$", "", regex=True)
    soja = soja.rename(columns={"nome_municipio": "nome_municipio_sidra"})

    # =========================
    # Garantir consistência de tipo da chave de merge
    # (evita erro silencioso de join)
    # =========================
    municipios["codigo_ibge"] = municipios["codigo_ibge"].astype(str)
    soja["codigo_ibge"] = soja["codigo_ibge"].astype(str)

    # =========================
    # Merge (LEFT JOIN)
    # Base territorial é soberana (645 municípios)
    # Municípios sem produção devem permanecer
    # =========================
    print("Realizando merge (LEFT JOIN)...")
    gdf = municipios.merge(
        soja[["codigo_ibge", "nome_municipio_sidra", "producao_ton"]],
        on="codigo_ibge",
        how="left"
    )

    print("Total municípios após merge:", len(gdf))

    # =========================
    # Municípios sem produção aparecem como NaN
    # Estratégia: considerar produção = 0
    # =========================
    print("Tratando municípios sem produção...")
    gdf["producao_ton"] = gdf["producao_ton"].fillna(0)

    # =========================
    # Cálculo da densidade territorial
    # Métrica macro: produção total / área municipal
    # =========================
    print("Calculando densidade territorial...")
    gdf["densidade_ton_km2"] = gdf["producao_ton"] / gdf["area_km2"]
    print("\nResumo estatístico da densidade (ton/km²):")
    print(gdf["densidade_ton_km2"].describe())


    # Separar municípios sem produção
    gdf["classe_densidade"] = "Sem produção"

    # Aplicar quartis apenas para densidade > 0
    mask = gdf["densidade_ton_km2"] > 0

    gdf.loc[mask, "classe_densidade"] = pd.qcut(
        gdf.loc[mask, "densidade_ton_km2"],
        q=3,
        labels=["Baixa", "Média", "Alta"]
    )
    print("\nDistribuição por classe de densidade:")
    print(gdf["classe_densidade"].value_counts())

    # =========================
    # Visualização rápida: Top 5 municípios
    # =========================
    print("\nTop 5 municípios por densidade (ton/km²):")
    top5 = (
        gdf.sort_values("densidade_ton_km2", ascending=False)
        [["nome_municipio", "densidade_ton_km2"]]
        .head()
    )
    print(top5)

    # =========================
    # Exportar resultados
    # GeoJSON: mantém geometria
    # CSV: versão tabular para análise
    # =========================
    print("\nSalvando outputs...")

    gdf.to_file(
        output_dir / "soja_densidade_sp.geojson",
        driver="GeoJSON"
    )

    gdf.drop(columns="geometry").to_csv(
        output_dir / "soja_densidade_sp.csv",
        index=False
    )

    print("Arquivos salvos na pasta /outputs")


if __name__ == "__main__":
    main()