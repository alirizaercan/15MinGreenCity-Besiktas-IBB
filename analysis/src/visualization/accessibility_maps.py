import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
from shapely.geometry import Point, Polygon
import networkx as nx
import osmnx as ox
import pandas as pd
import folium
import os

def create_15min_city_map():
    """Create interactive 15-minute city accessibility map"""
    # Load processed data
    bike_paths = gpd.read_file('data/processed/besiktas_bike_paths.geojson')
    micromobility = gpd.read_file('data/processed/besiktas_micromobility.geojson')
    
    # Load green areas and convert to GeoDataFrame with proper geometry
    green_areas = pd.read_excel('data/processed/besiktas_green_area_coordinates.xlsx')
    green_areas = gpd.GeoDataFrame(
        green_areas,
        geometry=gpd.points_from_xy(green_areas.LONGITUDE, green_areas.LATITUDE),
        crs="EPSG:4326"
    )
    
    # Load footways and convert any datetime columns to strings
    footways = gpd.read_file('data/raw/osm/besiktas_pedestrian_and_cycling_network.geojson')
    
    # Convert datetime columns to strings in all GeoDataFrames
    for df in [bike_paths, micromobility, footways]:
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].astype(str)
    
    # Create base map centered on Beşiktaş
    m = folium.Map(location=[41.0425, 29.005], zoom_start=14)
    
    # Add bike paths
    folium.GeoJson(
        bike_paths,
        name='Bike Paths',
        style_function=lambda x: {'color': 'blue', 'weight': 3}
    ).add_to(m)
    
    # Add micromobility stations
    for idx, row in micromobility.iterrows():
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=5,
            color='orange',
            fill=True,
            popup=row['Park_Alani']
        ).add_to(m)
    
    # Add green areas as markers
    for idx, row in green_areas.iterrows():
        folium.CircleMarker(
            location=[row.LATITUDE, row.LONGITUDE],
            radius=5,
            color='green',
            fill=True,
            fill_opacity=0.3,
            popup=row['MAHAL_ADI']
        ).add_to(m)
    
    # Add footways
    folium.GeoJson(
        footways.drop(columns=[col for col in footways.columns if col != 'geometry']),  # Keep only geometry
        name='Footways',
        style_function=lambda x: {'color': 'purple', 'weight': 2}
    ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Save map
    os.makedirs('outputs/maps', exist_ok=True)
    m.save('outputs/maps/besiktas_15min_city_map.html')
    print("Interactive map saved to outputs/maps/besiktas_15min_city_map.html")

if __name__ == "__main__":
    create_15min_city_map()