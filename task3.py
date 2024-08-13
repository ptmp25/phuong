import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import tkinter as tk
from matplotlib.lines import Line2D
from tkinter import ttk

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
    print(f"Total Length: {total_length:.2f} Kms")
    print(f"Average Distance: {average_distance:.2f} Kms")
    print(f"Standard Deviation: {std_distance:.2f} Kms")
    return total_length, average_distance, std_distance

def find_best_route(G, start_station, end_station):
    try:
        best_route = nx.dijkstra_path(G, start_station, end_station, weight='weight')
        best_distance = nx.dijkstra_path_length(G, start_station, end_station, weight='weight')
    except nx.NetworkXNoPath:
        best_route = None
        best_distance = float('inf')
    return best_route, best_distance

def plot_map(G, pos, df, total_length, average_distance, std_distance, best_route, best_distance):
    # plt.figure(figsize=(16, 9))
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
                bbox=dict(facecolor='w', edgecolor='none', alpha=0.3), 
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
    interchange_patch = Line2D([], [], marker='o', color='black', label='Interchange', markerfacecolor='white', markersize=5, linestyle='None')

    # Create a list of legend elements
    legend_elements = [interchange_patch]

    # Get the unique lines present in the data
    present_lines = df['Line'].unique()

    # Add line colors to the legend only for lines present in the data
    for line in present_lines:
        if line in colors:
            legend_elements.append(Line2D([0], [0], marker='o', color=colors[line], lw=2, label=f'{line} Line'))

    # Create the legend
    plt.legend(handles=legend_elements, loc='lower right', fontsize=10)
    rect = mpatches.Rectangle((0, 0), 1, 1, transform=plt.gca().transAxes, color='black', fill=False, linewidth=2)
    plt.gca().add_patch(rect)

    plt.title('London Tube Map')

    # Highlight best route
    if best_route:
        best_route_edges = list(zip(best_route[:-1], best_route[1:]))
        for i, edge in enumerate(best_route_edges):
            start_pos = offset_position(pos[edge[0]], i, len(best_route_edges))
            end_pos = offset_position(pos[edge[1]], i, len(best_route_edges))
            plt.plot([start_pos[0], end_pos[0]], [start_pos[1], end_pos[1]],
                     color='gold', linewidth=4, alpha=0.7,
                     label='Best Route' if i == 0 else "")
    
    # Add total length, average distance and standard deviation to the plot
    plt.text(0.02, 0.98, f'Total Length: {total_length:.2f} Kms', transform=plt.gca().transAxes, fontsize=10, ha='left', va='top')
    plt.text(0.02, 0.95, f'Average Distance: {average_distance:.2f} Kms', transform=plt.gca().transAxes, fontsize=10, ha='left', va='top')
    plt.text(0.02, 0.92, f'Standard Deviation: {std_distance:.2f} Kms', transform=plt.gca().transAxes, fontsize=10, ha='left', va='top')
    plt.text(0.02, 0.89, f'Best Distance: {best_distance:.2f} Kms', transform=plt.gca().transAxes, fontsize=10, ha='left', va='top')

    plt.axis('off')
    plt.tight_layout()
    plt.show()

def on_find_route():
    start_station = start_station_combobox.get()
    end_station = end_station_combobox.get()
    best_route, best_distance = find_best_route(g, start_station, end_station)
    if best_route:
        result_label.config(text=f"Best route from {start_station} to {end_station}:\n" + " -> ".join(best_route) + f"\nTotal distance: {best_distance:.2f} Kms")
    else:
        result_label.config(text=f"No path found from {start_station} to {end_station}")
    plot_map(g, pos, df, total_length, average_distance, std_distance, best_route, best_distance)

def offset_position(pos, index, total, max_offset=0.0001):
    if total == 1:
        return pos
    offset = (index - (total - 1) / 2) * max_offset
    return (pos[0] + offset, pos[1] + offset)

# Create a graph
g = nx.Graph()
plt.figure(figsize=(32, 18))

# Load data
station_coordinates = load_coordinates('stations.csv', '1')
df = load_data('distance.csv')

# Add edges and their distances
for _, row in df.iterrows():
    if (row['Station from (A)'] in station_coordinates) and (row['Station to (B)'] in station_coordinates):
        g.add_edge(row['Station from (A)'], row['Station to (B)'], weight=row['Distance (Kms)'], line=row['Line'])
    else:
        df.drop(index=_, inplace=True)

# Get positions for the nodes
pos = get_node_positions(g, station_coordinates)

# Calculate statistics
total_length, average_distance, std_distance = calculate_statistics(df)

# List of stations
stations = list(g.nodes())

# Tkinter GUI
root = tk.Tk()
root.title("Find Best Route")

tk.Label(root, text="Start Station:").grid(row=0)
tk.Label(root, text="End Station:").grid(row=1)

start_station_combobox = ttk.Combobox(root, values=stations, state='readonly')
end_station_combobox = ttk.Combobox(root, values=stations, state='readonly')

start_station_combobox.grid(row=0, column=1)
end_station_combobox.grid(row=1, column=1)

tk.Button(root, text="Find Route", command=on_find_route).grid(row=2, column=0, columnspan=2)

result_label = tk.Label(root, text="", wraplength=400)
result_label.grid(row=3, column=0, columnspan=2)

root.mainloop()
