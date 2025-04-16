import geopandas as gpd
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import os
import pandas as pd
from matplotlib.lines import Line2D
from shapely.geometry import Point

def create_walkability_network():
    """Create walkability network analysis for Beşiktaş with POI visualization"""
    # Create output directory
    os.makedirs('outputs/maps', exist_ok=True)
    
    # Get Beşiktaş boundary
    besiktas = ox.geocode_to_gdf("Beşiktaş, Istanbul, Turkey")
    
    # Create network graph for walking
    G = ox.graph_from_place(
        "Beşiktaş, Istanbul, Turkey",
        network_type='walk',
        truncate_by_edge=True
    )
    
    # Calculate basic stats
    stats = ox.basic_stats(G)
    print(f"Network stats: {stats}")
    
    return G, besiktas

def get_all_pois(boundary):
    """Get all POIs within Beşiktaş boundary from OpenStreetMap"""
    poi_categories = {
        'Healthcare': ['hospital', 'clinic', 'doctors', 'dentist', 'pharmacy', 'healthcare'],
        'Education': ['school', 'university', 'college', 'kindergarten', 'library'],
        'Transport': ['bus_stop', 'subway_entrance', 'ferry_terminal', 'taxi', 'bus_station'],
        'Public Services': ['police', 'fire_station', 'post_office', 'townhall', 'public_building'],
        'Markets': ['supermarket', 'marketplace', 'convenience', 'grocery', 'mall', 'department_store'],
        'Recreation': ['park', 'garden', 'sports_centre', 'playground', 'fitness_centre'],
        'Food': ['restaurant', 'cafe', 'fast_food', 'pub', 'bar'],
        'Culture': ['theatre', 'cinema', 'museum', 'arts_centre', 'gallery']
    }
    
    # Dictionary to store POIs by category
    all_pois = {}
    
    # For each category and its tags
    for category, tags in poi_categories.items():
        category_pois = []
        
        # For each tag in the category
        for tag in tags:
            # Create tag dictionary for OSMnx
            tags = {
                'amenity': tag,
                'building': tag,
                'shop': tag,
                'leisure': tag,
                'highway': tag,
                'railway': tag,
                'office': tag,
                'tourism': tag
            }
            
            # Get POIs
            try:
                # First try with specific tag
                pois = ox.features_from_polygon(boundary.iloc[0].geometry, tags)
                if not pois.empty:
                    pois['poi_type'] = tag
                    category_pois.append(pois)
            except (KeyError, ValueError, TypeError) as e:
                print(f"No POIs found for {tag} or error: {e}")
        
        # Combine all POIs for the category
        if category_pois:
            try:
                category_gdf = pd.concat(category_pois, ignore_index=True)
                all_pois[category] = category_gdf
                print(f"Found {len(category_gdf)} {category} POIs")
            except ValueError:
                print(f"No {category} POIs found")
    
    return all_pois

def visualize_pois(G, pois, boundary):
    """Visualize POIs with different colors and legend"""
    # Define colors and markers for each category
    category_styles = {
        'Healthcare': {'color': 'red', 'marker': 'o'},
        'Education': {'color': 'blue', 'marker': '^'},
        'Transport': {'color': 'green', 'marker': 'v'},
        'Public Services': {'color': 'orange', 'marker': 'd'},
        'Markets': {'color': 'brown', 'marker': '*'},
        'Recreation': {'color': 'lightgreen', 'marker': 'p'},
        'Food': {'color': 'purple', 'marker': 's'},
        'Culture': {'color': 'magenta', 'marker': 'h'}
    }
    
    # Create plot
    fig, ax = plt.subplots(figsize=(16, 14))
    
    # Plot the boundary
    boundary.plot(ax=ax, color='white', edgecolor='black', alpha=0.1)
    
    # Plot the base network
    ox.plot_graph(
        G, 
        ax=ax,
        node_size=0,
        edge_linewidth=0.5,
        edge_color='#333333',
        bgcolor='white',
        show=False
    )
    
    # Create legend elements list
    legend_elements = []
    
    # Plot each POI category
    for category, gdf in pois.items():
        if category in category_styles:
            style = category_styles[category]
            
            # Extract coordinates and plot
            for _, row in gdf.iterrows():
                if hasattr(row.geometry, 'x') and hasattr(row.geometry, 'y'):
                    ax.plot(
                        row.geometry.x, row.geometry.y,
                        marker=style['marker'],
                        markersize=8,
                        color=style['color'],
                        alpha=0.7,
                        linestyle='none'
                    )
            
            # Add to legend
            legend_elements.append(
                Line2D([0], [0], marker=style['marker'], color='w', 
                       label=f"{category} ({len(gdf)})",
                       markerfacecolor=style['color'], markersize=10)
            )
    
    # Add legend
    ax.legend(handles=legend_elements, loc='upper right', 
              title='POI Categories', fontsize='small')
    
    # Add title and adjust layout
    plt.title('15-Minute Walkability Analysis with POIs in Beşiktaş', fontsize=16)
    plt.tight_layout()
    
    # Save and show
    plt.savefig(
        'outputs/maps/besiktas_complete_poi_analysis.png',
        dpi=300,
        bbox_inches='tight',
        facecolor='white',
        transparent=False
    )
    plt.show()
    plt.close()

def analyze_poi_distribution(pois, boundary):
    """Analyze POI distribution and create summary statistics"""
    # Create a GeoDataFrame for all POIs
    all_pois_list = []
    
    for category, gdf in pois.items():
        gdf['category'] = category
        all_pois_list.append(gdf)
    
    if all_pois_list:
        all_pois_gdf = pd.concat(all_pois_list, ignore_index=True)
        
        # Count POIs per category
        category_counts = all_pois_gdf['category'].value_counts()
        
        # Calculate area in square kilometers
        area_km2 = boundary.iloc[0].geometry.area / 1e6
        
        # Calculate density per sq km
        density = {cat: count / area_km2 for cat, count in category_counts.items()}
        
        # Print stats
        print(f"\nPOI Distribution Analysis for Beşiktaş:")
        print(f"Total area: {area_km2:.2f} km²")
        print(f"Total POIs: {len(all_pois_gdf)}")
        print(f"Overall POI density: {len(all_pois_gdf) / area_km2:.2f} POIs per km²")
        print("\nCategory-wise distribution:")
        
        for category, count in category_counts.items():
            print(f"{category}: {count} POIs ({density[category]:.2f} per km²)")
        
        # Create a plot for POI distribution
        plt.figure(figsize=(12, 6))
        category_counts.plot(kind='bar', color='skyblue')
        plt.title('POI Distribution in Beşiktaş')
        plt.xlabel('Category')
        plt.ylabel('Number of POIs')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('outputs/maps/besiktas_poi_distribution.png', dpi=300)
        plt.close()

if __name__ == "__main__":
    # Create network and get boundary
    G, besiktas_boundary = create_walkability_network()
    
    # Get all POIs in Beşiktaş
    all_pois = get_all_pois(besiktas_boundary)
    
    # Visualize network with all POIs
    visualize_pois(G, all_pois, besiktas_boundary)
    
    # Analyze POI distribution
    analyze_poi_distribution(all_pois, besiktas_boundary)