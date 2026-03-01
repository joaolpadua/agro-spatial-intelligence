from pathlib import Path
import requests
import pandas as pd


def main():
    base_dir = Path(__file__).resolve().parent.parent
    processed_dir = base_dir / "data" / "processed"

    print("Iniciando coleta de dados de produção de soja...")


if __name__ == "__main__":
    main()