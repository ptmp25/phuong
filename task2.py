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
            station_coordinates[row['Station']] = (row['Longitude'], row['Latitude'])
    return station_coordinates

def get_node_positions(G, station_coordinates):
    default_position = (0, 0)  
    pos = {node: station_coordinates.get(node, default_position) for node in G.nodes()}
    return pos

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

# Add nodes to the graph
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

plt.figure(figsize=(24, 18))

# Draw the graph
# Draw the edges for each line with different colors and labels for each line 
for i, line in enumerate(lines):
    line_data = df[df['Line'] == line]
    edges = [(row['Station from (A)'], row['Station to (B)']) for _, row in line_data.iterrows()]
    nx.draw_networkx_edges(g, pos, edgelist=edges, edge_color=colors[line], width=2, label=f'{line} Line')

# Draw the nodes 
for node in g.nodes():
    # Find the line of the node
    for _, row in df.iterrows():
        if row['Station from (A)'] == node or row['Station to (B)'] == node:
            line = row['Line']
            break
    nx.draw_networkx_nodes(g, pos, nodelist=[node], node_color=colors[line], node_size=50)

# Draw the node labels 
for node, (x, y) in pos.items():
    plt.text(x, y, node, fontsize=10, ha='left', va='top', fontweight='bold', 
             bbox=dict(facecolor='white', edgecolor='none', alpha=0.3), rotation=-10)

# Draw the edge labels    
edge_labels = {(row['Station from (A)'], row['Station to (B)']): row['Distance (Kms)'] for _, row in df.iterrows()}
nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels, font_size=8, font_color='black')

plt.legend(loc='lower right', fontsize=10)
plt.title('London Tube Map')

plt.show()