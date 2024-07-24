import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# distances in kilometers 
distances = {
    ('Hyde Park Corner', 'Green Park'): 1.0,
    ('Green Park', 'Piccadilly Circus'): 0.5,
    ('Piccadilly Circus', 'Leicester Square'): 0.1,
    ('Leicester Square', 'Covent Garden'): 0.6,
    ('Covent Garden', 'Holborn'): 1.2
}

# Create a graph
G = nx.Graph()

# Add edges and their distances
for (station1, station2), distance in distances.items():
    G.add_edge(station1, station2, weight=distance)

# Get positions for the nodes (you can adjust these to improve the visualization)
pos = {
    'Hyde Park Corner': (-1, -1),
    'Green Park': (0.6, 1),
    'Piccadilly Circus': (2.6, 1),
    'Leicester Square': (3, 1),
    'Covent Garden': (4, 2),
    'Holborn': (5.5, 3.5)
}

# Add nodes to the graph
for station, position in pos.items():
    G.nodes[station]['pos'] = position

angle = 20
# Custom node labels
node_labels = {
    'Hyde Park Corner': ('Hyde Park Corner', 0, pos['Hyde Park Corner'][0] + 0.5, pos['Hyde Park Corner'][1]),
    'Green Park': ('Green Park', angle, pos['Green Park'][0] + 0.25, pos['Green Park'][1] + 0.25),
    'Piccadilly Circus': ('Piccadilly Circus', angle, pos['Piccadilly Circus'][0] + 0.3, pos['Piccadilly Circus'][1] + 0.25),
    'Leicester Square': ('Leicester Square', angle, pos['Leicester Square'][0] + 0.3, pos['Leicester Square'][1] -0.1),
    'Covent Garden': ('Covent Garden', 0, pos['Covent Garden'][0] + 0.5, pos['Covent Garden'][1]),
    'Holborn': ('Holborn', 0, pos['Holborn'][0] - 0.4, pos['Holborn'][1])
}

plt.figure(figsize=(12, 9))

# Draw the graph
pos = nx.get_node_attributes(G, 'pos')
edges = nx.draw_networkx_edges(G, pos, node_size=50,  edge_color='blue', width=2, label='Piccadilly Line')

nodes = nx.draw_networkx_nodes(G, pos, node_size=100, node_color='blue')

for (node, (label, angle, x, y)) in node_labels.items():
    plt.text(x, y, label, fontsize=8, rotation=angle, ha='center', va='center')

# Draw the edge labels
edge_labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, font_color='black')

# Add legend
plt.legend(scatterpoints=1, loc='lower right', ncol=1, fontsize=10)

# Add title
plt.title('Piccadilly Line - London Underground')

# Display plot
plt.show()
