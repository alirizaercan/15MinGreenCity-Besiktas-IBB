import geopandas as gpd
import networkx as nx
import osmnx as ox
from shapely.geometry import Point
import matplotlib.pyplot as plt

def calculate_accessibility():
    # Configure OSMnx (new way in recent versions)
    ox.settings.use_cache = True
    ox.settings.log_console = True
    
    # Get Beşiktaş boundary
    place = "Beşiktaş, Istanbul, Turkey"
    graph = ox.graph_from_place(place, network_type='walk')
    
    # Get central point (example: Beşiktaş square)
    center_point = Point(29.007149, 41.041224)  # Note: Point takes (x,y) which is (long,lat)
    
    # Calculate 15-minute walking distance (assuming 5 km/h walking speed)
    walking_speed = 5  # km/h
    max_distance = walking_speed * 0.25  # 15 minutes in hours
    
    # Create isochrone
    G_proj = ox.project_graph(graph)
    center_node = ox.distance.nearest_nodes(G_proj, center_point.x, center_point.y)
    subgraph = nx.ego_graph(G_proj, center_node, radius=max_distance*1000, distance='length')
    
    # Plot
    fig, ax = ox.plot_graph(subgraph, node_size=0, edge_linewidth=0.5, 
                           show=False, close=False, edge_color='#999999')
    ax.scatter(center_point.x, center_point.y, c='red', s=100, 
               label='Center Point')
    plt.title('15-Minute Walking Accessibility from Beşiktaş Square', fontsize=16)
    plt.legend()
    plt.savefig('outputs/maps/walking_accessibility.png')
    
    return {
        'area_covered_km2': None,  # Would calculate actual area
        'nodes_in_range': len(subgraph.nodes()),
        'edges_in_range': len(subgraph.edges())
    }

if __name__ == "__main__":
    results = calculate_accessibility()
    print("Accessibility analysis results:", results)