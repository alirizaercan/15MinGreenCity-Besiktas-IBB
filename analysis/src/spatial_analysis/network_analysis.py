import geopandas as gpd
import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import os

def create_walkability_network():
    """Create walkability network analysis for Beşiktaş"""
    # Çıktı dizinini oluştur
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
    
    # Plot network with customized settings
    fig, ax = plt.subplots(figsize=(12, 12))
    ox.plot_graph(
        G, 
        ax=ax,
        node_size=0, 
        edge_linewidth=0.5,
        edge_color='#333333',  # Daha koyu kenar çizgileri
        bgcolor='white'       # Arka plan rengi
    )
    
    # Kaydetmeden önce düzenlemeler
    plt.tight_layout()
    
    # Hem göster hem de kaydet
    plt.show()
    
    # Aynı görseli kaydet
    fig.savefig(
        'outputs/maps/walkability_network.png',
        dpi=300,
        bbox_inches='tight',
        facecolor=fig.get_facecolor(),  # Aynı arka plan rengini koru
        transparent=False
    )
    plt.close()
    
    return G

def calculate_accessibility(G, points_of_interest):
    """Calculate 15-minute walking accessibility"""
    # Convert POIs to nearest nodes
    pois_nodes = []
    for poi in points_of_interest:
        node = ox.distance.nearest_nodes(G, poi[1], poi[0])
        pois_nodes.append(node)
    
    # Calculate service areas
    service_areas = {}
    for node in pois_nodes:
        subgraph = nx.ego_graph(G, node, radius=1200, distance='length')  # ~15 min walk
        service_areas[node] = subgraph
    
    return service_areas

if __name__ == "__main__":
    G = create_walkability_network()
    # Example POIs (latitude, longitude)
    pois = [(41.0425, 29.005), (41.045, 29.01)]  # Replace with actual POIs
    service_areas = calculate_accessibility(G, pois)