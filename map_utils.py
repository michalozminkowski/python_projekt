import osmnx as ox
import numpy as np
import pandas as pd
from shapely.geometry import LineString
from scipy.spatial import KDTree
import config, csv


def get_grid_coords(lon, lat, min_x, max_x, min_y, max_y, grid_size):
    """Przelicza współrzędne GPS na piksele mapy (x, y)."""
    x = int((lon - min_x) / (max_x - min_x) * (grid_size - 1))
    y = int((1 - (lat - min_y) / (max_y - min_y)) * (grid_size - 1))
    return max(0, min(grid_size - 1, x)), max(0, min(grid_size - 1, y))


def load_traffic_points(csv_path):
    """Wczytuje słownik punktów korkowych z pliku CSV."""
    points = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            lat, lon = row['Współrzędne'].split(',')
            values = [float(row[f"{h:02d}:00"]) for h in range(24)]
            points[(float(lon), float(lat))] = values
    return points


def create_smog_map_with_congestion(csv_path=None):
    """Główna funkcja generująca mapę statyczną i macierz korków."""

    # 1. POBRANIE GEOMETRII Z OPENSTREETMAP
    graph = ox.graph_from_place(config.PLACE_NAME, network_type='drive')
    nodes, edges = ox.graph_to_gdfs(graph)
    min_x, min_y, max_x, max_y = edges.total_bounds

    smog_grid = np.zeros((config.GRID_SIZE, config.GRID_SIZE))
    congestion_grid = np.ones((24, config.GRID_SIZE, config.GRID_SIZE))
    label_candidates = {}

    # 2. PRZYGOTOWANIE STRUKTURY DANYCH TOMTOM (KDTREE)
    if csv_path:
        traffic_points = load_traffic_points(csv_path)
        tree = KDTree(list(traffic_points.keys()))
        traffic_values = list(traffic_points.values())

    # 3. PĘTLA PO WSZYSTKICH ODCINKACH DRÓG
    for index, row in edges.iterrows():
        # A. Obliczanie wagi emisji (Typ drogi + Pasy + Tramwaje)
        road_type = row['highway'][0] if isinstance(row['highway'], list) else row['highway']
        base_val = config.EMISSION_BASE.get(road_type, 0)
        if base_val == 0: continue

        lanes = float(row['lanes'][0]) if 'lanes' in row and isinstance(row['lanes'], list) else 1
        lane_multiplier = 1.0 + (max(1, lanes) - 1) * 0.6
        emission_value = base_val * lane_multiplier

        # B. Rasteryzacja (Rysowanie linii na macierzy)
        if isinstance(row['geometry'], LineString):
            coords = list(row['geometry'].coords)
            for i in range(len(coords) - 1):
                # Konwersja współrzędnych
                gx1, gy1 = get_grid_coords(coords[i][0], coords[i][1], min_x, max_x, min_y, max_y, config.GRID_SIZE)
                gx2, gy2 = get_grid_coords(coords[i + 1][0], coords[i + 1][1], min_x, max_x, min_y, max_y,
                                           config.GRID_SIZE)

                # Rysowanie linii piksel po pikselu
                num = max(abs(gx2 - gx1), abs(gy2 - gy1)) + 1
                xs = np.linspace(gx1, gx2, num).astype(int)
                ys = np.linspace(gy1, gy2, num).astype(int)
                valid = (xs >= 0) & (xs < config.GRID_SIZE) & (ys >= 0) & (ys < config.GRID_SIZE)

                for x, y in zip(xs[valid], ys[valid]):
                    smog_grid[y, x] = max(smog_grid[y, x], emission_value)

                    # C. Przypisanie danych TomTom (Najbliższy sąsiad)
                    if csv_path:
                        grid_lon = min_x + (x / config.GRID_SIZE) * (max_x - min_x)
                        grid_lat = max_y - (y / config.GRID_SIZE) * (max_y - min_y)
                        _, idx = tree.query([grid_lon, grid_lat])

                        for h in range(24):
                            congestion_grid[h, y, x] = 1.0 + (traffic_values[idx][h] / 100.0)

        # 4. GENEROWANIE PODPISÓW ULIC (Logika: Najdłuższy odcinek, Kąt 0)
        if 'name' in row and str(row['name']) != 'nan':
            name = str(row['name'][0]) if isinstance(row['name'], list) else str(row['name'])

            # Warunki: niepusta nazwa, długość > 50m, jakakolwiek emisja
            if len(name) > 2 and row['length'] > 50 and emission_value > 1:
                # Jeśli mamy już tę ulicę, ale znaleźliśmy dłuższy fragment -> nadpisz
                if name in label_candidates and row['length'] <= label_candidates[name]['length']:
                    continue

                centroid = row['geometry'].centroid
                cx, cy = get_grid_coords(centroid.x, centroid.y, min_x, max_x, min_y, max_y, config.GRID_SIZE)

                label_candidates[name] = {
                    'x': cx, 'y': cy,
                    'angle': 0,  # Wymuszony poziom
                    'length': row['length']
                }

    return smog_grid, label_candidates, congestion_grid