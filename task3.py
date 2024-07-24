import tkinter as tk
from tkinter import ttk
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
        plt.text(x, y, node, fontsize=5, ha='left', va='bottom')
    # Draw the edge labels    
    edge_labels = {(row['Station from (A)'], row['Station to (B)']): row['Distance (Kms)'] for _, row in df.iterrows()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=5, font_color='black')

    # Highlight best route
    if best_route:
        best_route_edges = list(zip(best_route[:-1], best_route[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=best_route_edges, edge_color='gold', width=3, label='Best Route')

    plt.legend(loc='lower right', fontsize=10)
    plt.title('London Tube Map')
    # Add total length, average distance and standard deviation to the plot
    plt.text(0.02, 0.02, f'Total Length: {total_length:.2f} Kms', transform=plt.gca().transAxes, fontsize=10)
    plt.text(0.02, 0.05, f'Average Distance: {average_distance:.2f} Kms', transform=plt.gca().transAxes, fontsize=10)
    plt.text(0.02, 0.08, f'Standard Deviation: {std_distance:.2f} Kms', transform=plt.gca().transAxes, fontsize=10)
    plt.text(0.02, 0.11, f'Best Distance: {best_distance:.2f} Kms', transform=plt.gca().transAxes, fontsize=10)

    plt.savefig('tube_map_with_best_route.png')
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

# List of stations
stations = list(station_coordinates.keys())

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
