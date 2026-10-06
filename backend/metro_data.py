"""
metro_data.py
Bangalore Metro (Namma Metro) Network Dataset and Graph Representation.

This module stores the stations, lines, colors, connections,
and realistic segment distances for the Bangalore Metro system.
"""

from typing import Dict, List, Any, Optional

# Color palette for Metro lines (matches existing frontend theme)
LINE_COLORS: Dict[str, str] = {
    "Purple": "#a855f7",
    "Green": "#22c55e",
    "Yellow": "#facc15",
    "Pink": "#ec4899"
}

# Line Station Sequences
# Reused and verified against the existing project dataset
PURPLE_LINE: List[str] = [
    "Challaghatta", "Kengeri", "Kengeri Bus Terminal", "Pattanagere", "Jnanabharathi",
    "Rajarajeshwari Nagar", "Pantharapalya - Nayandahalli", "Mysuru Road",
    "Deepanjali Nagar", "Attiguppe", "Vijayanagar",
    "Sri Balagangadharanatha Swamiji Station, Hosahalli", "Magadi Road",
    "Krantivira Sangolli Rayanna Railway Station",
    "Nadaprabhu Kempegowda Station", "Sir M. Visvesvaraya Station",
    "Dr. B. R. Ambedkar Station, Vidhana Soudha",
    "Cubbon Park", "Mahatma Gandhi Road", "Trinity", "Halasuru",
    "Indiranagar", "Swami Vivekananda Road", "Baiyappanahalli",
    "Benniganahalli", "KR Pura", "Singayyanapalya", "Garudacharpalya",
    "Hoodi", "Seetharamapalya", "Kundalahalli", "Nallurhalli",
    "Sri Sathya Sai Hospital", "Pattandur Agrahara",
    "Kadugodi Tree Park", "Hopefarm Channasandra", "Whitefield"
]

GREEN_LINE: List[str] = [
    "Madavara", "Chikkabidarakallu", "Manjunatha Nagara", "Nagasandra",
    "Dasarahalli", "Jalahalli", "Peenya Industry", "Peenya",
    "Goragunte Palya", "Yeshwanthpur", "Sandal Soap Factory",
    "Mahalakshmi", "Rajajinagar", "Mahakavi Kuvempu Road",
    "Srirampura", "Mantri Square Sampige Road",
    "Nadaprabhu Kempegowda Station",
    "Chickpete", "Krishna Rajendra Market", "National College",
    "Lalbagh", "South End Circle", "Jayanagara",
    "Rashtreeya Vidyalaya Road", "Banashankari",
    "Jaya Prakash Nagar", "Yelachenahalli", "Konanakunte Cross",
    "Doddakallasandra", "Vajarahalli", "Thalaghattapura", "Silk Institute"
]

YELLOW_LINE: List[str] = [
    "Rashtreeya Vidyalaya Road", "Ragigudda", "Jayadeva Hospital",
    "BTM Layout", "Central Silk Board", "Bommanahalli",
    "Hongasandra", "Kudlu Gate", "Singasandra", "Hosa Road",
    "Beratena Agrahara", "Electronic City", "Infosys Foundation",
    "Konappana Agrahara", "Huskur Road", "Biocon",
    "Hebbagodi", "Delta Electronics", "Bommasandra"
]

PINK_LINE: List[str] = [
    "Kalena Agrahara", "Hulimavu", "IIMB", "JP Nagar 4th Phase",
    "Jayadeva Hospital", "Tavarekere", "Dairy Circle", "Lakkasandra",
    "Langford Town", "National Military School", "Mahatma Gandhi Road",
    "Shivajinagar", "Cantonment", "Pottery Town", "Tannery Road",
    "Venkateshpura", "Kadugundanahalli", "Nagawara"
]

METRO_LINES: Dict[str, List[str]] = {
    "Purple": PURPLE_LINE,
    "Green": GREEN_LINE,
    "Yellow": YELLOW_LINE,
    "Pink": PINK_LINE
}

# Common user aliases / colloquial names for popular stations
STATION_ALIASES: Dict[str, str] = {
    "majestic": "Nadaprabhu Kempegowda Station",
    "kempegowda": "Nadaprabhu Kempegowda Station",
    "kempegowda station": "Nadaprabhu Kempegowda Station",
    "majestic station": "Nadaprabhu Kempegowda Station",
    "nadaprabhu kempegowda": "Nadaprabhu Kempegowda Station",
    "mg road": "Mahatma Gandhi Road",
    "m.g. road": "Mahatma Gandhi Road",
    "m g road": "Mahatma Gandhi Road",
    "rv road": "Rashtreeya Vidyalaya Road",
    "r.v. road": "Rashtreeya Vidyalaya Road",
    "r v road": "Rashtreeya Vidyalaya Road",
    "ksr railway station": "Krantivira Sangolli Rayanna Railway Station",
    "bangalore city railway station": "Krantivira Sangolli Rayanna Railway Station",
    "vidhana soudha": "Dr. B. R. Ambedkar Station, Vidhana Soudha",
    "kuvempu road": "Mahakavi Kuvempu Road",
    "hosahalli": "Sri Balagangadharanatha Swamiji Station, Hosahalli",
    "jayadeva": "Jayadeva Hospital",
    "silk board": "Central Silk Board",
    "ecity": "Electronic City",
    "electronic city": "Electronic City",
    "jp nagar": "Jaya Prakash Nagar",
    "jayanagar": "Jayanagara",
    "kr market": "Krishna Rajendra Market"
}

def normalize_station_name(name: str) -> Optional[str]:
    """
    Resolve station name or common aliases to canonical station name.
    Case-insensitive matching.
    """
    if not name:
        return None
    cleaned = name.strip()
    
    # Direct case-insensitive match against all known stations
    all_stations = get_all_stations()
    for st in all_stations:
        if st.lower() == cleaned.lower():
            return st
            
    # Check alias dictionary
    alias_key = cleaned.lower()
    if alias_key in STATION_ALIASES:
        return STATION_ALIASES[alias_key]

    # Substring matching fallback (e.g. "Yeshwanthpur" in "Yeshwanthpur Station")
    for st in all_stations:
        if cleaned.lower() in st.lower() or st.lower() in cleaned.lower():
            return st

    return None

def get_all_stations() -> List[str]:
    """Returns a sorted list of unique station names across all lines."""
    stations = set()
    for line_stations in METRO_LINES.values():
        stations.update(line_stations)
    return sorted(list(stations))

def get_lines_for_station(station: str) -> List[str]:
    """Returns all metro lines that serve a given station."""
    lines = []
    for line_name, line_stations in METRO_LINES.items():
        if station in line_stations:
            lines.append(line_name)
    return lines

def build_metro_graph() -> Dict[str, List[Dict[str, Any]]]:
    """
    Constructs the Bangalore Metro graph representation as an adjacency list.
    
    Structure:
    {
        "StationA": [
            {"to": "StationB", "line": "Purple", "distance": 1.4, "time": 2.2},
            ...
        ]
    }
    
    Average distance per station segment in Namma Metro is ~1.3 km.
    Average travel time per station segment is ~2.2 minutes (including deceleration & stop).
    """
    graph: Dict[str, List[Dict[str, Any]]] = {}
    
    for station in get_all_stations():
        graph[station] = []

    for line_name, stations in METRO_LINES.items():
        for i in range(len(stations) - 1):
            st_a = stations[i]
            st_b = stations[i + 1]
            
            # Default realistic distance (km) and travel time (minutes)
            segment_distance = 1.3
            segment_time = 2.2

            # Specific distance adjustments for longer inter-station stretches
            if (st_a == "Baiyappanahalli" and st_b == "Benniganahalli") or (st_b == "Baiyappanahalli" and st_a == "Benniganahalli"):
                segment_distance = 2.1
                segment_time = 3.5
            elif (st_a == "Mysuru Road" and st_b == "Pantharapalya - Nayandahalli") or (st_b == "Mysuru Road" and st_a == "Pantharapalya - Nayandahalli"):
                segment_distance = 1.8
                segment_time = 3.0

            # Add bidirectional edges
            graph[st_a].append({
                "to": st_b,
                "line": line_name,
                "distance": segment_distance,
                "time": segment_time
            })
            graph[st_b].append({
                "to": st_a,
                "line": line_name,
                "distance": segment_distance,
                "time": segment_time
            })

    return graph
