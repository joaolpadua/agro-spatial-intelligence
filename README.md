# Agro Spatial Intelligence  
### Territorial Density Analysis of Soybean Production – São Paulo (2021)

This project analyzes soybean production in São Paulo using a territorial density approach instead of traditional total-volume ranking.

Instead of asking *"who produces more?"*, we ask:

> How concentrated is soybean production within each municipality's territory?

---

## 🎯 Objective

To build a structured geospatial pipeline that:

- Collects official agricultural production data (IBGE – SIDRA API)
- Integrates municipal territorial boundaries
- Calculates territorial production density (ton/km²)
- Classifies municipalities statistically
- Generates analytical outputs and visualization

This project demonstrates practical spatial data engineering applied to agribusiness intelligence.

---

## 🧠 Methodological Approach

### 1️⃣ Territorial Base

- Municipal boundaries (São Paulo – 2024)
- Reprojected to **SIRGAS 2000 / UTM Zone 23S (EPSG:31983)**
- Area recalculated in km² for analytical consistency

---

### 2️⃣ Agricultural Data

Source: IBGE – Produção Agrícola Municipal (PAM)  
Table: 1612  
Product: Soybean (Soja em grão)  
Year: 2021  
Variable: Quantidade produzida (Toneladas)

Data collected directly from SIDRA API.

---

### 3️⃣ Density Calculation

Territorial density was calculated as:

```python
densidade_ton_km2 = producao_ton / area_km2
```

This shifts the analysis from absolute production to spatial intensity.

---

### 4️⃣ Statistical Classification

Municipalities with zero production were isolated before classification.

Quantile classification (q=3) was applied only to positive density values, generating:

Baixa

Média

Alta

This prevents distortion caused by structural zeros and ensures stable segmentation.

Final categories:

Sem produção

Baixa

Média

Alta

---

### 📊 Key Insights

Production density is strongly concentrated in the southwest region of São Paulo.

Coastal municipalities show structural absence of soybean production.

Several municipalities rank high in territorial density despite not leading in total volume.

Density-based ranking provides different strategic insights compared to total production ranking.

--- 

### 🗺️ Final Output

Categorical territorial density map:
![Soybean Density Map](outputs/mapa_soja_densidade_sp.png)

### 🏗️ Project Structure

```
soy_density_sp/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── outputs/
│   ├── soja_densidade_sp.geojson
│   ├── soja_densidade_sp.csv
│   └── mapa_soja_densidade_sp.png
│
├── scripts/
│   ├── 01_processa_municipios.py
│   ├── 02_processa_soja.py
│   ├── 03_merge_densidade.py
│   └── 04_gera_mapa.py
│
├── requirements.txt
└── README.md
```
---

### ⚙️ Pipeline Overview

Process municipal shapefile

Fetch soybean production data via API

Merge datasets

Compute territorial density

Classify municipalities

Generate map and export outputs

---

### 🛠️ Technologies Used

Python 3.11

Pandas

GeoPandas

Matplotlib

Requests

IBGE SIDRA API

Git / GitHub

---

### 📌 Why This Matters

- Credit allocation  
- Risk modeling  
- Logistics planning  
- Regional investment strategy  
- Land-use intensity evaluation  

---

### 🚀 Author

João Luiz de Pádua

Geospatial Data | Agribusiness Intelligence | Spatial Analytics

---