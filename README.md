# 15MinGreenCity-Besiktas-IBB

**A Data-Driven Project for Climate-Resilient 15-Minute City Transformation in Beşiktaş, Istanbul**

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)

## 📌 Project Overview

This project aims to transform Beşiktaş, Istanbul, into a **15-minute city** by optimizing walkability, cycling infrastructure, and green spaces. By leveraging open data from İBB, TÜİK, and OpenStreetMap (OSM), we propose low-cost, climate-friendly urban mobility solutions.

## 🎯 Project Objectives

1. **Reduce Carbon Emissions:** Promote sustainable transportation by encouraging biking and walking over motorized transport.
2. **Enhance Accessibility:** Ensure 80% of residents can access essential services within 15 minutes by foot or bicycle.
3. **Improve Climate Resilience:** Integrate green spaces to mitigate urban heat island effects and enhance urban livability.

## 📂 Project Structure

```
.
├───analysis
│   └───src
│       ├───data_processing
│       │       besiktas_data_processing.py
│       │       besiktas_tuik_data_processing.py
│       │
│       ├───spatial_analysis
│       │       accessibility_analysis.py
│       │       network_analysis.py
│       │
│       ├───statistical_analysis
│       │       green_space_analysis.py
│       │       mobility_analysis.py
│       │       population_analysis.py
│       │
│       └───visualization
│               accessibility_maps.py
│               __init__.py
│
├───assets
│   └───fonts
│           DejaVuSansCondensed (various font files)
│
├───cache
│
├───data
│   ├───processed
│   │       besiktas_bike_paths.geojson
│   │       besiktas_district_population_processed.xlsx
│   │       besiktas_green_area_coordinates.xlsx
│   │       besiktas_green_area_info.xlsx
│   │       besiktas_micromobility.geojson
│   │       besiktas_population_age_gender.xlsx
│   │       besiktas_population_by_district.xlsx
│   │       nationwide_population_age_gender_processed.xlsx
│   │
│   └───raw
│       ├───ibb
│       │       bisiklet_mikromobilite.geojson
│       │       istanbul-kentsel-acik-ve-yesil-alan-koordinatlar.xlsx
│       │       istanbul-kentsel_acik_yesil-alan-bilgileri.xlsx
│       │       istanbul_bisiklet_yollari.geojson
│       │
│       ├───osm
│       │       besiktas_pedestrian_and_cycling_network.geojson
│       │
│       └───tuik
│               il _ve_ilcelere gore il_ilce merkezi belde_koy_nufusu_ve_yillik_nufus_artis_hizi.xls
│               yas_grubu_ve_cinsiyete_gore il_ilce_merkezi_ve_belde_koy_nufusu.xls
│
├───docs
│
├───logs
│       green_space_analysis.log
│       population_analysis.log
│       processing.log
│
└───outputs
    ├───maps
    │       besiktas_15min_city_map.html
    │       bike_paths_by_year.png
    │       bike_path_types.png
    │       comprehensive_population_greenspace_analysis.png
    │       green_space_distribution.png
    │       green_space_types.png
    │       mobility_infrastructure.png
    │       walkability_network.png
    │       walking_accessibility.png
    │
    └───reports
            besiktas_mobility_analysis.pdf
            besiktas_population_green_space_analysis.pdf
```

## 📚 Dependencies

The project uses the following Python libraries:

```python
# Geospatial Analysis
import geopandas as gpd
from shapely.geometry import Point, Polygon
import osmnx as ox
from pyproj import CRS
import folium
import contextily as ctx

# Network Analysis
import networkx as nx

# Data Processing & Analysis
import pandas as pd
import numpy as np
from geopy.distance import geodesic

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.lines import Line2D

# Reporting
from fpdf import FPDF
from datetime import datetime

# System & Utilities
import os
import logging
```

## 🛠️ Project Setup

### Prerequisites

- Python 3.9+
- Git
- pip

### Installation Steps

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/alirizaercan/15MinGreenCity-Besiktas-IBB.git
   cd 15MinGreenCity-Besiktas-IBB
   ```

2. **Create Virtual Environment (Optional but Recommended):**
   ```bash
   python3.9 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🗺️ Data Processing and Analysis Workflow

### Data Processing
- Process raw IBB and TUIK data using `besiktas_data_processing.py` and `besiktas_tuik_data_processing.py`
- Convert and clean various datasets into GeoJSON and Excel formats

### Spatial Analysis
- Perform accessibility analysis with `accessibility_analysis.py`
- Conduct network analysis with `network_analysis.py` for walkability and cycling infrastructure

### Statistical Analysis
- Analyze green spaces with `green_space_analysis.py`
- Evaluate mobility patterns using `mobility_analysis.py`
- Analyze population demographics with `population_analysis.py`

### Visualization
- Generate maps and visualizations with `accessibility_maps.py`

## 📊 Key Outputs

The project generates several outputs:

### Maps
- Interactive 15-minute city accessibility map: `besiktas_15min_city_map.html`
- Bike path analysis: `bike_paths_by_year.png`, `bike_path_types.png`
- Green space analysis: `green_space_distribution.png`, `green_space_types.png`
- Walkability and mobility: `walkability_network.png`, `walking_accessibility.png`, `mobility_infrastructure.png`

### Reports
- Comprehensive population and green space analysis: `besiktas_population_green_space_analysis.pdf`
- Mobility infrastructure analysis: `besiktas_mobility_analysis.pdf`

## 🔒 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## 🙌 Contributing

Contributions are welcome! 

- Open an issue to discuss proposed changes
- Submit a Pull Request with your improvements
- Follow project coding standards

## 📞 Contact

For questions or collaboration, please open an issue in the GitHub repository.