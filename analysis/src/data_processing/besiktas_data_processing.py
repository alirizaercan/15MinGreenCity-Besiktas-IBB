import geopandas as gpd
import pandas as pd
import os
from pathlib import Path

def setup_directories():
    """Create necessary directories if they don't exist"""
    os.makedirs("data/processed", exist_ok=True)

def process_geojson_files():
    """Process GeoJSON files from IBB"""
    try:
        # Bike paths
        bike_paths = gpd.read_file("data/raw/ibb/istanbul_bisiklet_yollari.geojson")
        besiktas_bike_paths = bike_paths[
            (bike_paths["ILCE_1"].str.upper() == "BEŞİKTAŞ") | 
            (bike_paths["ILCE_2"].str.upper() == "BEŞİKTAŞ")
        ]
        besiktas_bike_paths.to_file("data/processed/besiktas_bike_paths.geojson", driver="GeoJSON")
        
        # Micromobility
        micromobility = gpd.read_file("data/raw/ibb/bisiklet_mikromobilite.geojson")
        besiktas_micromobility = micromobility[micromobility["Ilce"].str.upper() == "BEŞİKTAŞ"]
        besiktas_micromobility.to_file("data/processed/besiktas_micromobility.geojson", driver="GeoJSON")
    except Exception as e:
        print(f"Error processing GeoJSON files: {e}")

def process_ibb_xlsx_files():
    """Process XLSX files from IBB"""
    try:
        # Green area info
        green_area_info = pd.read_excel("data/raw/ibb/istanbul-kentsel_acik_yesil-alan-bilgileri.xlsx")
        green_area_info.to_excel("data/processed/besiktas_green_area_info.xlsx", index=False)
        
        # Green area coordinates
        green_area_coords = pd.read_excel("data/raw/ibb/istanbul-kentsel-acik-ve-yesil-alan-koordinatlar.xlsx")
        besiktas_green_areas = green_area_coords[green_area_coords["ILCE"].str.upper() == "BEŞİKTAŞ"]
        besiktas_green_areas.to_excel("data/processed/besiktas_green_area_coordinates.xlsx", index=False)
    except Exception as e:
        print(f"Error processing IBB XLSX files: {e}")

def process_tuik_xls_files():
    """Process XLS files from TUIK"""
    try:
        # Population by district - this contains district-level data
        pop_district = pd.read_excel(
            "data/raw/tuik/il _ve_ilcelere gore il_ilce merkezi belde_koy_nufusu_ve_yillik_nufus_artis_hizi.xls",
            engine='xlrd'
        )
        
        # Find the district column (handles different naming)
        district_col = next((col for col in pop_district.columns if "ilçe" in col.lower() or "district" in col.lower()), None)
        
        if district_col:
            # Filter for Beşiktaş
            besiktas_pop = pop_district[pop_district[district_col].str.contains("BEŞİKTAŞ", na=False, case=False)]
            besiktas_pop.to_excel("data/processed/besiktas_population_by_district.xlsx", index=False)
        else:
            print("Could not find district column in population file")
        
        # Population by age and gender - handle the complex header structure
        pop_age_gender = pd.read_excel(
            "data/raw/tuik/yas_grubu_ve_cinsiyete_gore il_ilce_merkezi_ve_belde_koy_nufusu.xls",
            engine='xlrd',
            header=None  # Read without header first
        )
        
        # The actual header is in row 4 (0-indexed)
        # Create proper multi-index header
        header_rows = [4, 5, 6]  # Rows containing header information
        
        # Read the file again with proper header rows
        pop_age_gender = pd.read_excel(
            "data/raw/tuik/yas_grubu_ve_cinsiyete_gore il_ilce_merkezi_ve_belde_koy_nufusu.xls",
            engine='xlrd',
            header=header_rows
        )
        
        # Clean up column names
        pop_age_gender.columns = [
            'Year',
            'Age Group',
            'Total Population',
            'Male',
            'Female',
            'Urban Total',
            'Urban Male',
            'Urban Female',
            'Rural Total',
            'Rural Male',
            'Rural Female'
        ]
        
        # Drop rows that are entirely null (like the title rows we skipped)
        pop_age_gender = pop_age_gender.dropna(how='all')
        
        # Create a dictionary with metadata
        metadata = {
            "description": "This file contains NATIONWIDE population data by age and gender (2007-2024)",
            "source": "TÜİK (Turkish Statistical Institute)",
            "note": "For Beşiktaş-specific population data, see besiktas_population_by_district.xlsx",
            "columns": {
                "Year": "Year of data",
                "Age Group": "Age group category",
                "Total Population": "Total population count",
                "Male": "Male population count",
                "Female": "Female population count",
                "Urban Total": "Total urban population",
                "Urban Male": "Male urban population",
                "Urban Female": "Female urban population",
                "Rural Total": "Total rural population",
                "Rural Male": "Male rural population",
                "Rural Female": "Female rural population"
            }
        }
        
        # Convert to DataFrame and save with metadata
        with pd.ExcelWriter("data/processed/besiktas_population_age_gender.xlsx") as writer:
            pop_age_gender.to_excel(
                writer, 
                sheet_name="Population Data", 
                index=False,
                header=True
            )
            
            # Add metadata sheet
            pd.DataFrame.from_dict(metadata, orient='index').to_excel(
                writer, 
                sheet_name="README",
                header=False
            )
            
    except Exception as e:
        print(f"Error processing TUIK XLS files: {e}")
        
        
def process_osm_data():
    """Process OSM data"""
    try:
        osm_data = gpd.read_file("data/raw/osm/besiktas_pedestrian_and_cycling_network.geojson")
        osm_data.to_file("data/processed/besiktas_osm_parks_paths.geojson", driver="GeoJSON")
    except Exception as e:
        print(f"Error processing OSM data: {e}")

def main():
    print("Setting up directories...")
    setup_directories()
    
    print("Processing GeoJSON files...")
    process_geojson_files()
    
    print("Processing IBB XLSX files...")
    process_ibb_xlsx_files()
    
    print("Processing TUIK XLS files...")
    process_tuik_xls_files()
    
    print("Processing OSM data...")
    process_osm_data()
    
    print("All data processing completed. Check the 'processed' folder for results.")

if __name__ == "__main__":
    main()