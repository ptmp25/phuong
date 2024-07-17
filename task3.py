import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

def load_data(file_path):
    data = pd.read_csv(file_path, encoding='latin1')
    return data

def load_coordinates(coordinates_file, zone='1'):
    coordinates_data = pd.read_csv(coordinates_file)
    station_coordinates = {}
    for _, row in coordinates_data.iterrows():
        if row['Zone'] == zone:
            station_coordinates[row['Station']] = (row['OS X'], row['OS Y'])
    return station_coordinates

def get_node_positions(G, station_coordinates):
    default_position = (0, 0)  
    pos = {node: station_coordinates.get(node, default_position) for node in G.nodes()}
    return pos

def calculate_statistics(df):
    total_length = df['Distance (Kms)'].sum()
    average_distance = df['Distance (Kms)'].mean()
    std_distance = df['Distance (Kms)'].std()
    return total_length, average_distance, std_distance

def find_best_route(G, start_station, end_station):
    try:
        best_route = nx.dijkstra_path(G, start_station, end_station, weight='weight')
        best_distance = nx.dijkstra_path_length(G, start_station, end_station, weight='weight')
    except nx.NetworkXNoPath:
        best_route = None
        best_distance = float('inf')
    return best_route, best_distance

# Create a graph
g = nx.Graph()
g.figsize = (12, 9)

# Load data
station_coordinates = load_coordinates('stations.csv', '1')
df = load_data('all - Copy.csv')

# Add edges and their distances
for _, row in df.iterrows():
    # Check if both stations are in the coordinates data
    if (row['Station from (A)'] in station_coordinates) and (row['Station to (B)'] in station_coordinates):
        g.add_edge(row['Station from (A)'], row['Station to (B)'], weight=row['Distance (Kms)'], line=row['Line'])
    else:
        df.drop(index=_, inplace=True)
        
# Get positions for the nodes
pos = get_node_positions(g, station_coordinates)

# Calculate statistics
total_length, average_distance, std_distance = calculate_statistics(df)

# Input stations
start_station = 'CHANCERY LANE'  # Replace with actual station name
end_station = 'OLD STREET'    # Replace with actual station name

# Find best route
best_route, best_distance = find_best_route(g, start_station, end_station)

# Print the route
if best_route:
    print(f"Best route from {start_station} to {end_station}:")
    for i in range(len(best_route) - 1):
        print(f"{best_route[i]} -> {best_route[i + 1]}: {g[best_route[i]][best_route[i + 1]]['weight']} Kms")
    print(f"Total distance: {best_distance:.2f} Kms")
else:
    print(f"No path found from {start_station} to {end_station}")

# Visualization
plt.figure(figsize=(24, 18))

# Draw the edges for each line with different colors and labels for each line 
lines = df['Line'].unique()
colors = {
    'Bakerloo ': 'brown',
    'Central ': 'red',
    'Circle ': 'yellow',
    'District': 'green',
    'Jubilee ': 'grey',
    'Metropolitan': 'purple',
    'Northern ': 'black',
    'Piccadilly ': 'blue',
    'Victoria': 'lightblue',
    'H & C': 'pink',
    'Waterloo & City': 'lightgreen', 
    'DLR': 'orange',
}

for line in lines:
    line_data = df[df['Line'] == line]
    edges = [(row['Station from (A)'], row['Station to (B)']) for _, row in line_data.iterrows()]
    nx.draw_networkx_edges(g, pos, edgelist=edges, edge_color=colors[line], width=2, label=f'{line} Line')

# Draw the nodes 
nx.draw_networkx_nodes(g, pos, node_size=10, node_color='black')
# Draw the node labels 
for node, (x, y) in pos.items():
    plt.text(x, y, node, fontsize=5, ha='left', va='bottom')
# Draw the edge labels    
edge_labels = {(row['Station from (A)'], row['Station to (B)']): row['Distance (Kms)'] for _, row in df.iterrows()}
nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels, font_size=5, font_color='black')

# Highlight best route
if best_route:
    best_route_edges = list(zip(best_route[:-1], best_route[1:]))
    nx.draw_networkx_edges(g, pos, edgelist=best_route_edges, edge_color='gold', width=3, label='Best Route')

plt.legend(loc='lower right', fontsize=10)
plt.title('London Tube Map')
# Add total length, average distance and standard deviation to the plot
plt.text(0.02, 0.02, f'Total Length: {total_length:.2f} Kms', transform=plt.gca().transAxes, fontsize=10)
plt.text(0.02, 0.05, f'Average Distance: {average_distance:.2f} Kms', transform=plt.gca().transAxes, fontsize=10)
plt.text(0.02, 0.08, f'Standard Deviation: {std_distance:.2f} Kms', transform=plt.gca().transAxes, fontsize=10)
plt.text(0.02, 0.11, f'Best Distance: {best_distance:.2f} Kms', transform=plt.gca().transAxes, fontsize=10)

plt.savefig('tube_map_with_best_route.png')
plt.show()
