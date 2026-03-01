from pathlib import Path
import requests
import pandas as pd


def main():
    base_dir = Path(__file__).resolve().parent.parent
    processed_dir = base_dir / "data" / "processed"
    processed_dir.mkdir(exist_ok=True)

    url = (
        "https://servicodados.ibge.gov.br/api/v3/agregados/1612/"
        "periodos/2021/variaveis/214"
        "?localidades=N6[all]"
        "&classificacao=81[2713]"
    )

    print("Consultando API SIDRA (Tabela 1612 - Soja 2021)...")

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    data = response.json()

    # Extrair séries
    series = data[0]["resultados"][0]["series"]

    registros = []

    for item in series:
        codigo = item["localidade"]["id"]
        nome = item["localidade"]["nome"]
        valor = item["serie"]["2021"]

        registros.append({
            "codigo_ibge": codigo,
            "nome_municipio": nome,
            "producao_ton": valor
        })

    df = pd.DataFrame(registros)

    print("\nTotal registros:", len(df))

    # Converter produção para numérico
    df["producao_ton"] = pd.to_numeric(df["producao_ton"], errors="coerce")

    # Filtrar apenas SP (códigos começam com 35)
    df_sp = df[df["codigo_ibge"].str.startswith("35")].copy()

    print("Municípios SP encontrados:", len(df_sp))

    # Salvar CSV
    output_path = processed_dir / "soja_sp_2021.csv"
    df_sp.to_csv(output_path, index=False)

    print("Arquivo salvo em:", output_path)


if __name__ == "__main__":
    main()