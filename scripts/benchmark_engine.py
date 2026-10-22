import csv
import math
import time
import statistics
import random
from collections import deque
import heapq
import os

EARTH_RADIUS_KM = 6371.0

def haversine(lat1_rad, lon1_rad, lat2_rad, lon2_rad):
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat / 2.0)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2.0)**2
    c = 2.0 * math.asin(math.sqrt(min(1.0, max(0.0, a))))
    return EARTH_RADIUS_KM * c

def load_graph(dataset_dir):
    airports = {}
    airports_path = os.path.join(dataset_dir, "airports.csv")
    with open(airports_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            iata = row["iata"]
            lat = float(row["latitude"])
            lon = float(row["longitude"])
            airports[iata] = {
                "name": row["name"],
                "city": row["city"],
                "country": row["country"],
                "lat": lat,
                "lon": lon,
                "lat_rad": math.radians(lat),
                "lon_rad": math.radians(lon),
            }

    adj = {iata: [] for iata in airports}
    routes_path = os.path.join(dataset_dir, "routes_unique.csv")
    with open(routes_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            src = row["source_airport"]
            dst = row["destination_airport"]
            if src in airports and dst in airports:
                dist = float(row["distance_km"])
                minutes = (dist / 800.0) * 60.0 + 30.0
                adj[src].append((dst, dist, minutes))

    return airports, adj

def bfs_reachability(adj, origin, destination, max_legs=3):
    start_time = time.perf_counter()
    if origin not in adj or destination not in adj:
        return False, None, [], 0, (time.perf_counter() - start_time) * 1000.0

    queue = deque([(origin, 0, [origin])])
    visited = {origin: 0}
    nodes_visited = 0

    while queue:
        current, legs, path = queue.popleft()
        nodes_visited += 1

        if current == destination:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return True, legs - 1, path, nodes_visited, elapsed_ms

        if legs < max_legs:
            for neighbor, _, _ in adj.get(current, []):
                if neighbor not in visited or visited[neighbor] > legs + 1:
                    visited[neighbor] = legs + 1
                    queue.append((neighbor, legs + 1, path + [neighbor]))

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    return False, None, [], nodes_visited, elapsed_ms

def astar_fastest_path(airports, adj, origin, destination, max_legs=3):
    start_time = time.perf_counter()
    if origin not in airports or destination not in airports:
        return False, None, [], 0, (time.perf_counter() - start_time) * 1000.0

    dest_lat = airports[destination]["lat_rad"]
    dest_lon = airports[destination]["lon_rad"]

    def heuristic(u):
        u_lat = airports[u]["lat_rad"]
        u_lon = airports[u]["lon_rad"]
        dist = haversine(u_lat, u_lon, dest_lat, dest_lon)
        return (dist / 800.0) * 60.0

    initial_h = heuristic(origin)
    pq = [(initial_h, 0.0, 0, origin, [origin])]
    best_g = {}
    nodes_expanded = 0

    while pq:
        f_score, g_score, legs, current, path = heapq.heappop(pq)
        nodes_expanded += 1

        if current == destination:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return True, g_score, path, nodes_expanded, elapsed_ms

        state_key = (current, legs)
        if state_key in best_g and best_g[state_key] <= g_score:
            continue
        best_g[state_key] = g_score

        if legs < max_legs:
            for neighbor, dist, flight_minutes in adj.get(current, []):
                layover = 60.0 if current != origin else 0.0
                new_g = g_score + flight_minutes + layover
                new_legs = legs + 1
                neighbor_state = (neighbor, new_legs)

                if neighbor_state not in best_g or new_g < best_g[neighbor_state]:
                    h = heuristic(neighbor)
                    new_f = new_g + h
                    heapq.heappush(pq, (new_f, new_g, new_legs, neighbor, path + [neighbor]))

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    return False, None, [], nodes_expanded, elapsed_ms

def pareto_filter(offers):
    front = []
    for a in offers:
        dominated = False
        for b in offers:
            if b["id"] == a["id"]:
                continue
            if b["price"] <= a["price"] and b["duration"] <= a["duration"] and b["stops"] <= a["stops"]:
                if b["price"] < a["price"] or b["duration"] < a["duration"] or b["stops"] < a["stops"]:
                    dominated = True
                    break
        if not dominated:
            front.append(a)
    return front

def multicriteria_rank(front, alpha=0.5, beta=0.3, gamma=0.2):
    if not front:
        return []
    prices = [o["price"] for o in front]
    durations = [o["duration"] for o in front]
    stops_list = [o["stops"] for o in front]

    p_min, p_max = min(prices), max(prices)
    t_min, t_max = min(durations), max(durations)
    s_min, s_max = min(stops_list), max(stops_list)

    ranked = []
    for o in front:
        p_prime = (o["price"] - p_min) / (p_max - p_min) if p_max > p_min else 0.0
        t_prime = (o["duration"] - t_min) / (t_max - t_min) if t_max > t_min else 0.0
        e_prime = (o["stops"] - s_min) / (s_max - s_min) if s_max > s_min else 0.0
        score = math.sqrt(alpha * (p_prime**2) + beta * (t_prime**2) + gamma * (e_prime**2))
        affinity = round((1.0 - score) * 100)
        ranked.append({**o, "score": score, "affinity": affinity})

    ranked.sort(key=lambda x: (x["score"], x["price"], x["duration"]))
    return ranked

def generate_synthetic_offers(n, base_duration_min=180.0):
    offers = []
    for i in range(n):
        stops = random.choice([0, 1, 2])
        price = random.uniform(200.0, 950.0) - (stops * 70.0) + random.uniform(-30.0, 30.0)
        price = max(120.0, price)
        duration = base_duration_min + (stops * 180.0) + random.uniform(0.0, 120.0)
        offers.append({
            "id": f"off_{i+1}",
            "price": round(price, 2),
            "duration": round(duration, 1),
            "stops": stops,
            "route": f"seq_{stops}"
        })
    return offers

def main():
    dataset_dir = "docs/backend-documentation/navby-datasets"
    airports, adj = load_graph(dataset_dir)

    test_cases = [
        ("Caso 1 (Troncal Directo)", "LIM", "SCL", "Lima -> Santiago"),
        ("Caso 2 (Continental 1 Escala)", "LIM", "EZE", "Lima -> Buenos Aires"),
        ("Caso 3 (Intercontinental 2 Escalas)", "LIM", "NRT", "Lima -> Tokio Narita"),
        ("Caso 4 (Metropolitano Transatlántico)", "LHR", "JFK", "Londres -> Nueva York"),
        ("Caso 5 (Inviable en <= 2 Escalas)", "AYP", "AAT", "Ayacucho -> Altay"),
    ]

    print("=== BENCHMARK DE CASOS DE PRUEBA (100 ITERACIONES POR CASO) ===")
    results_cases = []
    for name, orig, dest, desc in test_cases:
        bfs_times = []
        astar_times = []
        bfs_nodes = 0
        astar_nodes = 0
        bfs_res = None
        astar_res = None

        for _ in range(100):
            b_reach, b_stops, b_path, b_vis, b_t = bfs_reachability(adj, orig, dest, max_legs=3)
            bfs_times.append(b_t)
            bfs_nodes = b_vis
            bfs_res = (b_reach, b_stops, b_path)

            a_reach, a_tmin, a_path, a_exp, a_t = astar_fastest_path(airports, adj, orig, dest, max_legs=3)
            astar_times.append(a_t)
            astar_nodes = a_exp
            astar_res = (a_reach, a_tmin, a_path)

        b_mean = statistics.mean(bfs_times)
        b_std = statistics.stdev(bfs_times)
        a_mean = statistics.mean(astar_times)
        a_std = statistics.stdev(astar_times)

        results_cases.append({
            "name": name,
            "orig": orig,
            "dest": dest,
            "desc": desc,
            "bfs_reach": "Sí" if bfs_res[0] else "No",
            "bfs_stops": str(bfs_res[1]) if bfs_res[1] is not None else "—",
            "bfs_path": " $\\rightarrow$ ".join(bfs_res[2]) if bfs_res[2] else "Inalcanzable",
            "bfs_nodes": bfs_nodes,
            "bfs_ms": b_mean,
            "bfs_std": b_std,
            "astar_reach": "Sí" if astar_res[0] else "No",
            "astar_tmin": f"{astar_res[1]:.1f}" if astar_res[1] else "—",
            "astar_path": " $\\rightarrow$ ".join(astar_res[2]) if astar_res[2] else "Inalcanzable",
            "astar_nodes": astar_nodes,
            "astar_ms": a_mean,
            "astar_std": a_std,
        })

    print("\n| Caso de Prueba | Par | Escalas | T_min (min) | Ruta Óptima A* | Nodos A* | Tiempo BFS (ms) | Tiempo A* (ms) |")
    print("| :--- | :---: | :---: | :---: | :--- | :---: | :---: | :---: |")
    for r in results_cases:
        print(f"| {r['name']} | {r['orig']} $\\rightarrow$ {r['dest']} | {r['bfs_stops']} | {r['astar_tmin']} | {r['astar_path']} | {r['astar_nodes']} | {r['bfs_ms']:.2f} $\\pm$ {r['bfs_std']:.2f} | {r['astar_ms']:.2f} $\\pm$ {r['astar_std']:.2f} |")

    print("\n=== ESCALABILIDAD DEL MOTOR MULTICRITERIO (100 ITERACIONES POR N) ===")
    sample_sizes = [10, 25, 50, 100, 200, 500]
    pareto_results = []
    random.seed(42)

    print("\n| Cantidad de Ofertas ($N$) | Tiempo Promedio (ms) | Desviación Estándar (ms) | Tamaño Promedio Frontera |")
    print("| :---: | :---: | :---: | :---: |")
    for n in sample_sizes:
        times = []
        front_sizes = []
        for _ in range(100):
            offers = generate_synthetic_offers(n)
            t0 = time.perf_counter()
            front = pareto_filter(offers)
            ranked = multicriteria_rank(front)
            t1 = time.perf_counter()
            times.append((t1 - t0) * 1000.0)
            front_sizes.append(len(front))

        mean_ms = statistics.mean(times)
        std_ms = statistics.stdev(times)
        mean_front = statistics.mean(front_sizes)
        print(f"| {n} | {mean_ms:.3f} | {std_ms:.3f} | {mean_front:.1f} |")

if __name__ == "__main__":
    main()
