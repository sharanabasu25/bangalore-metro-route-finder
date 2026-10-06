"""
route_finder.py
Graph Search Algorithms for Bangalore Metro Route Planning.

This module implements:
1. Dijkstra's Shortest Path Algorithm (optimized for travel time & line transfers)
2. Breadth-First Search (BFS) for minimal station hops
3. Fare, distance, and interchange calculation engines

Viva / Academic Notes:
- Time Complexity (Dijkstra): O((V + E) * log(V)) where V is stations (nodes) and E is metro track links (edges).
- Space Complexity (Dijkstra): O(V) for visited set and priority queue.
- Time Complexity (BFS): O(V + E)
- Space Complexity (BFS): O(V)
"""

import heapq
from collections import deque
from typing import Dict, List, Any, Optional, Tuple

try:
    from backend.metro_data import (
        build_metro_graph,
        get_all_stations,
        normalize_station_name,
        LINE_COLORS
    )
except ImportError:
    from metro_data import (
        build_metro_graph,
        get_all_stations,
        normalize_station_name,
        LINE_COLORS
    )

# Penalty in minutes added when a commuter has to switch platforms at an interchange
INTERCHANGE_PENALTY_MINUTES = 5.0

def calculate_fare(stops: int) -> int:
    """
    Computes Bangalore Metro fare based on number of stops traveled.
    Standard Namma Metro fare matrix slab.
    """
    if stops <= 0:
        return 0
    if stops <= 2:
        return 10
    if stops <= 4:
        return 20
    if stops <= 6:
        return 30
    if stops <= 8:
        return 40
    if stops <= 10:
        return 50
    if stops <= 16:
        return 60
    if stops <= 18:
        return 70
    if stops <= 26:
        return 80
    return 90

class MetroRouteFinder:
    """
    Intelligent Route Finder engine using graph algorithms.
    """

    def __init__(self):
        # Graph Adjacency List: { station: [ {to, line, distance, time}, ... ] }
        self.graph = build_metro_graph()
        self.all_stations = get_all_stations()

    def find_route_dijkstra(self, start: str, end: str) -> Optional[Dict[str, Any]]:
        """
        Calculates the optimal route using Dijkstra's Algorithm.
        Considers travel time and penalizes line changes (interchanges).
        
        Priority Queue items:
        (accumulated_time, current_station, current_line, path_nodes, path_edges, accumulated_distance)
        """
        # Priority Queue (min-heap)
        # Entry: (cost_time, station, current_line, path, edge_history, total_dist)
        pq: List[Tuple[float, str, Optional[str], List[str], List[Dict[str, Any]], float]] = []
        heapq.heappush(pq, (0.0, start, None, [start], [], 0.0))

        # Best cost tracker: (station, current_line) -> lowest time seen
        best_cost: Dict[Tuple[str, Optional[str]], float] = {}
        best_cost[(start, None)] = 0.0

        while pq:
            curr_time, curr_st, curr_line, path, edges, curr_dist = heapq.heappop(pq)

            # Destination reached
            if curr_st == end:
                return self._format_route_result(
                    start=start,
                    end=end,
                    route=path,
                    edges=edges,
                    total_time=curr_time,
                    total_dist=curr_dist,
                    algorithm="Dijkstra's Algorithm (Weighted by Time & Interchange)"
                )

            # Skip if we already found a faster way to this (station, line) state
            if curr_time > best_cost.get((curr_st, curr_line), float('inf')):
                continue

            for edge in self.graph.get(curr_st, []):
                neighbor = edge["to"]
                next_line = edge["line"]
                seg_time = edge["time"]
                seg_dist = edge["distance"]

                # Apply interchange penalty if commuter changes lines
                transfer_penalty = 0.0
                if curr_line is not None and curr_line != next_line:
                    transfer_penalty = INTERCHANGE_PENALTY_MINUTES

                next_time = curr_time + seg_time + transfer_penalty
                next_dist = curr_dist + seg_dist

                # Check if this path to neighbor on next_line is better
                state_key = (neighbor, next_line)
                if next_time < best_cost.get(state_key, float('inf')):
                    best_cost[state_key] = next_time
                    new_path = path + [neighbor]
                    new_edges = edges + [{"from": curr_st, "to": neighbor, "line": next_line, "distance": seg_dist, "time": seg_time}]
                    heapq.heappush(pq, (next_time, neighbor, next_line, new_path, new_edges, next_dist))

        return None

    def find_route_bfs(self, start: str, end: str) -> Optional[Dict[str, Any]]:
        """
        Finds shortest route in terms of minimum number of stations (stops)
        using Breadth-First Search (BFS).
        """
        # Queue stores: (current_station, path, edges_list)
        queue = deque([(start, [start], [])])
        visited = {start}

        while queue:
            curr_st, path, edges = queue.popleft()

            if curr_st == end:
                total_time = sum(e["time"] for e in edges)
                total_dist = sum(e["distance"] for e in edges)
                # Count interchanges to add transfer time
                changes = self._extract_interchanges(path, edges)
                total_time += len(changes) * INTERCHANGE_PENALTY_MINUTES

                return self._format_route_result(
                    start=start,
                    end=end,
                    route=path,
                    edges=edges,
                    total_time=total_time,
                    total_dist=total_dist,
                    algorithm="Breadth-First Search (BFS - Fewest Stations)"
                )

            for edge in self.graph.get(curr_st, []):
                neighbor = edge["to"]
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = path + [neighbor]
                    new_edges = edges + [{"from": curr_st, "to": neighbor, "line": edge["line"], "distance": edge["distance"], "time": edge["time"]}]
                    queue.append((neighbor, new_path, new_edges))

        return None

    def _extract_interchanges(self, route: List[str], edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifies stations where the user must switch between metro lines."""
        interchanges = []
        if len(edges) < 2:
            return interchanges

        for i in range(len(edges) - 1):
            if edges[i]["line"] != edges[i + 1]["line"]:
                interchanges.append({
                    "station": edges[i]["to"],
                    "from_line": edges[i]["line"],
                    "to_line": edges[i + 1]["line"]
                })
        return interchanges

    def _format_route_result(
        self,
        start: str,
        end: str,
        route: List[str],
        edges: List[Dict[str, Any]],
        total_time: float,
        total_dist: float,
        algorithm: str
    ) -> Dict[str, Any]:
        """Formats the calculated graph path into a rich, structured dictionary."""
        stops = max(0, len(route) - 1)
        fare = calculate_fare(stops)
        interchanges = self._extract_interchanges(route, edges)

        # Build detailed segment step-by-step
        path_details = []
        for i, st in enumerate(route):
            line_for_station = None
            if i == 0 and edges:
                line_for_station = edges[0]["line"]
            elif i > 0 and i - 1 < len(edges):
                line_for_station = edges[i - 1]["line"]

            is_interchange = any(c["station"] == st for c in interchanges)
            
            path_details.append({
                "station": st,
                "line": line_for_station,
                "color": LINE_COLORS.get(line_for_station, "#8b5cf6") if line_for_station else "#8b5cf6",
                "is_interchange": is_interchange,
                "is_start": (i == 0),
                "is_end": (i == len(route) - 1)
            })

        return {
            "source": start,
            "destination": end,
            "route": route,
            "stations": stops,
            "total_stations_count": len(route),
            "estimated_time": round(total_time),
            "distance": round(total_dist, 1),
            "fare": fare,
            "interchanges": interchanges,
            "interchanges_count": len(interchanges),
            "algorithm": algorithm,
            "path_details": path_details
        }

    def plan_journey(self, source: str, destination: str, preferred_algo: str = "dijkstra") -> Dict[str, Any]:
        """
        Validates input and plans the optimal metro journey.
        """
        # Resolve aliases
        canonical_src = normalize_station_name(source)
        canonical_dst = normalize_station_name(destination)

        if not canonical_src:
            raise ValueError(f"Unknown or invalid source station: '{source}'")
        if not canonical_dst:
            raise ValueError(f"Unknown or invalid destination station: '{destination}'")
        if canonical_src == canonical_dst:
            raise ValueError("Source and destination cannot be the same station.")

        if preferred_algo.lower() == "bfs":
            result = self.find_route_bfs(canonical_src, canonical_dst)
        else:
            result = self.find_route_dijkstra(canonical_src, canonical_dst)

        if not result:
            raise RuntimeError(f"No reachable metro route found between {canonical_src} and {canonical_dst}.")

        return result
