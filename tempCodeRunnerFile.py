import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

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

def offset_position(pos, index, total, max_offset=0.00005):
    if total == 1:
        return pos
    offset = (index - (total - 1) / 2) * max_offset
    return (pos[0] + offset, pos[1] + offset)

# Create a graph
g = nx.MultiGraph()

plt.figure(figsize=(16, 9))

# Load data
station_coordinates = load_coordinates('stations.csv', '1')
df = load_data('distance.csv')

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

# Group edges by stations
edge_lines = {}
for _, row in df.iterrows():
    key = (row['Station from (A)'], row['Station to (B)'])
    if key not in edge_lines:
        edge_lines[key] = []
    edge_lines[key].append(row['Line'])

# Draw the edges for each line with different colors and labels for each line
for edge, lines_on_edge in edge_lines.items():
    for i, line in enumerate(lines_on_edge):
        start_pos = offset_position(pos[edge[0]], i, len(lines_on_edge))
        end_pos = offset_position(pos[edge[1]], i, len(lines_on_edge))
        plt.plot([start_pos[0], end_pos[0]], [start_pos[1], end_pos[1]],
                 color=colors[line], linewidth=2, alpha=0.7,
                 label=f'{line} Line' if line not in plt.gca().get_legend_handles_labels()[1] else "")

# Remove duplicate labels
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))

# Count the number of lines each station is part of
station_line_count = {}
for _, row in df.iterrows():
    for station in [row['Station from (A)'], row['Station to (B)']]:
        if station not in station_line_count:
            station_line_count[station] = set()
        station_line_count[station].add(row['Line'])

# Draw the nodes
for node in g.nodes():
    # Determine if the node is part of multiple lines
    if len(station_line_count[node]) > 1:
        nx.draw_networkx_nodes(g, pos, nodelist=[node], node_color='white', edgecolors='black', node_size=300, linewidths=1.5)
    else:
        # Find the color of the node
        for _, row in df.iterrows():
            if row['Station from (A)'] == node or row['Station to (B)'] == node:
                node_color = colors[row['Line']]
                break
        nx.draw_networkx_nodes(g, pos, nodelist=[node], node_color=node_color, node_size=50)

# Draw the node labels
for node, (x, y) in pos.items():
    plt.text(x, y, node, fontsize=5, ha='right', va='top', fontweight='bold', 
             bbox=dict(facecolor='yellow', edgecolor='none', alpha=0.3), 
             rotation=20)
    
# Draw the edge labels
edge_labels = {}
for _, row in df.iterrows():
    key = (row['Station from (A)'], row['Station to (B)'])
    if key in edge_labels:
        edge_labels[key] += f"\n{row['Line']}: {row['Distance (Kms)']}"
    else:
        edge_labels[key] = f"{row['Line']}: {row['Distance (Kms)']}"

for (node1, node2), label in edge_labels.items():
    x = (pos[node1][0] + pos[node2][0]) / 2
    y = (pos[node1][1] + pos[node2][1]) / 2
    plt.text(x, y, label, fontsize=6, ha='center', va='top',
             bbox=dict(facecolor='white', edgecolor='none', alpha=0))

# Create a Patch for the interchangeable stations
interchange_patch = mpatches.Patch(facecolor='white', edgecolor='black', label='Interchangeable Stations')

# Create a list of legend elements
legend_elements = [interchange_patch]

# Get the unique lines present in the data
present_lines = df['Line'].unique()

# Add line colors to the legend only for lines present in the data
for line in present_lines:
    if line in colors:
        legend_elements.append(mpatches.Patch(color=colors[line], label=f'{line} Line'))

# Create the legend
plt.legend(handles=legend_elements, loc='lower right', fontsize=10)

# Draw a rectangle around the plot area
rect = mpatches.Rectangle((0, 0), 1, 1, transform=plt.gca().transAxes, color='black', fill=False, linewidth=2)
plt.gca().add_patch(rect)

def calculate_statistics(df):
    total_length = df['Distance (Kms)'].sum()
    average_distance = df['Distance (Kms)'].mean()
    std_distance = df['Distance (Kms)'].std()
    print(f"Total Length: {total_length:.2f} Kms")
    print(f"Average Distance: {average_distance:.2f} Kms")
    print(f"Standard Deviation: {std_distance:.2f} Kms")
    return total_length, average_distance, std_distance

# Calculate statistics
total_length, average_distance, std_distance = calculate_statistics(df)

# Add total length, average distance and standard deviation to the plot
plt.text(0.02, 0.98, f'Total Length: {total_length:.2f} Kms', transform=plt.gca().transAxes, fontsize=10, ha='left', va='top')
plt.text(0.02, 0.95, f'Average Distance: {average_distance:.2f} Kms', transform=plt.gca().transAxes, fontsize=10, ha='left', va='top')
plt.text(0.02, 0.92, f'Standard Deviation: {std_distance:.2f} Kms', transform=plt.gca().transAxes, fontsize=10, ha='left', va='top')

plt.title('London Tube Map')
plt.axis('off')  # Turn off the axis
plt.tight_layout()
plt.show()
