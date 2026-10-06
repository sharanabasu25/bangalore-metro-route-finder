# Bangalore Metro Route Finder Using Python, Graph Algorithms and Generative AI

An intelligent web-based commute planning application for the Bengaluru Metro (Namma Metro) network. The system calculates optimal paths using classic graph theory algorithms (**Dijkstra's Algorithm** and **Breadth-First Search**) on a Python Flask backend, and synthesizes commuter-friendly, natural-language route explanations using **Google Gemini Generative AI**.

---

## 1. Project Overview

**Bangalore Metro Route Finder** is an interactive, full-stack college mini-project that bridges fundamental Computer Science concepts (Graph Data Structures & Shortest Path Algorithms) with modern Artificial Intelligence (Generative AI).

The application allows commuters to:
1. Select source and destination stations across Bangalore's operational and upcoming metro corridors (Purple, Green, Yellow, and Pink lines).
2. Choose between **Dijkstra's Algorithm** (time and line-change weighted) or **Breadth-First Search (BFS)** (minimal station stops).
3. View immediate metrics including total stops, travel time, travel distance, ticket fare, and required line changes.
4. Interact with an **AI Metro Assistant** that answers queries in plain English without hallucinating routes.

---

## 2. Problem Statement

Finding an efficient metro route between two stations can be challenging in a rapidly expanding metropolitan transit network like Bangalore, particularly when travelers are unfamiliar with line intersections (e.g., Majestic, RV Road, MG Road, Jayadeva Hospital) and transfer requirements. 

Traditional map applications often present raw lists of stops without contextual advice or natural-language explanations. This project provides an integrated system that determines the exact shortest path mathematically and translates it into an intuitive, human-friendly travel guide using Generative AI.

---

## 3. Objectives

- **Python-Based Backend:** Build a lightweight, scalable RESTful API using Flask.
- **Graph Representation:** Model Bangalore Metro stations as graph vertices (nodes) and tracks as weighted bidirectional edges.
- **Shortest-Path Algorithms:** Implement both Dijkstra's Algorithm (optimizing for time and interchange delays) and Breadth-First Search (BFS) for minimal station hops.
- **Interactive Web Interface:** Provide a responsive, glassmorphic UI using HTML5, CSS3, and JavaScript that retains the project's original aesthetic.
- **Generative AI Integration:** Integrate Google Gemini AI to translate deterministic graph data into conversational commute advice.
- **Fault-Tolerant Design:** Ensure clean offline fallback capabilities when third-party AI keys or network connections are absent.

---

## 4. Features

- 🚇 **Comprehensive Station Network:** Covers 100+ stations across Purple, Green, Yellow, and Pink lines.
- ⚡ **Dual Graph Algorithms:**
  - **Dijkstra's Algorithm:** Calculates the quickest travel time while factoring in a 5-minute penalty for line interchanges.
  - **Breadth-First Search (BFS):** Calculates the path with the fewest total station stops.
- 💰 **Automated Fare Calculation:** Accurately calculates official Bangalore Metro fare slabs (₹10 to ₹90).
- 🔄 **Interchange Detection:** Flags transfer stations and indicates from which line to which line the commuter must switch.
- 🤖 **Ground-Truth Generative AI Assistant:**
  - AI answers are strictly grounded in calculated graph data to eliminate hallucinations.
  - Answers natural queries such as *"How do I travel from Indiranagar to MG Road?"* or *"Which station should I change at?"*.
  - Built-in intelligent offline fallback mode if `GEMINI_API_KEY` is not configured.
- ⇄ **Station Swapper & Prompt Chips:** One-click swapping of source and destination, plus pre-built prompt chips for quick queries.
- 🛡️ **Robust Input Validation:** Rejects invalid, identical, or unselected stations with user-friendly alerts.

---

## 5. System Architecture

```
[ Commuter Browser ]
        │
        │ 1. HTTP Request (Source, Destination, Algorithm)
        ▼
[ Flask REST API (app.py) ]
        │
        │ 2. Queries Graph Network
        ▼
[ Graph Engine (route_finder.py & metro_data.py) ]
        │ ── Builds Adjacency List
        │ ── Executes Dijkstra / BFS
        │ ── Calculates Distance, Time, Fare, Interchanges
        ▼
[ Verified Route Data (Ground Truth JSON) ]
        │
        ├──▶ 3a. Returns Direct JSON to Frontend
        │
        ▼
[ AI Assistant Engine (ai_assistant.py) ]
        │ ── Prompts Google Gemini API with Ground-Truth Facts
        │ ── Generates Commuter Narrative & Travel Advice
        ▼
[ Frontend Display (script.js + index.html) ]
        │ ── Visual Station Sequence
        │ ── Metric Badges (Time, Distance, Fare, Stops)
        │ ── AI Explanation Card
```

---

## 6. Technologies Used

### Frontend
- **HTML5:** Semantic layout and structure.
- **CSS3 (Vanilla):** Custom glassmorphism, responsive CSS grid, flexbox layout, and CSS variables.
- **JavaScript (ES6+):** Fetch API for asynchronous backend communication, dynamic DOM manipulation.

### Backend
- **Python 3.11:** Core logic and algorithm execution.
- **Flask 3.x:** Lightweight RESTful API server.
- **Flask-CORS:** Cross-Origin Resource Sharing support.
- **python-dotenv:** Environment variable configuration.

### Algorithms & Data Structures
- **Graph Adjacency List:** Station nodes with weighted edges (distance, time, line).
- **Dijkstra's Algorithm:** Priority Queue (`heapq`) based shortest path.
- **Breadth-First Search (BFS):** Queue (`collections.deque`) based traversal.

### Generative AI
- **Google Gemini API (`gemini-1.5-flash`):** Natural-language route synthesis and conversational guidance.
- **Deterministic Rule Engine:** Offline fallback synthesizer.

### Development & Tools
- **Git & GitHub:** Version control.
- **Visual Studio Code / Antigravity IDE:** Integrated development environment.

---

## 7. Graph Algorithm Explanation

### Graph Data Structure
The metro network is represented as an **Adjacency List**:
- **Vertices ($V$):** Each unique metro station (e.g., `Majestic`, `Indiranagar`, `Yeshwanthpur`).
- **Edges ($E$):** Bidirectional tracks connecting consecutive stations.
- **Edge Attributes:**
  - `to`: Adjacent station name
  - `line`: Metro corridor (Purple, Green, Yellow, Pink)
  - `distance`: Segment distance in kilometers (~1.3 km avg)
  - `time`: Segment travel time in minutes (~2.2 mins avg)

### 1. Dijkstra's Algorithm (Weighted Shortest Path)
- **Objective:** Find the path minimizing total travel time.
- **Interchange Penalty:** If transitioning from Line $A$ to Line $B$, a 5.0-minute transfer penalty is added to the accumulated cost.
- **Mechanism:**
  1. Initialize a min-heap priority queue with `(0, start_node, current_line, path, edges, dist)`.
  2. Greedily extract the state with minimum accumulated time.
  3. If destination is extracted, return the route.
  4. For all adjacent nodes, relax edge weights if a shorter arrival time is discovered.
- **Time Complexity:** $\mathcal{O}((V + E) \log V)$
- **Space Complexity:** $\mathcal{O}(V)$

### 2. Breadth-First Search (Fewest Station Stops)
- **Objective:** Find the path with the minimum number of station hops, regardless of time or distance.
- **Mechanism:** Explores nodes level-by-level using a FIFO queue (`collections.deque`).
- **Time Complexity:** $\mathcal{O}(V + E)$
- **Space Complexity:** $\mathcal{O}(V)$

---

## 8. Generative AI Explanation

### Strict Grounding Architecture
Large Language Models (LLMs) can hallucinate station sequences or invent nonexistent connections. To guarantee 100% route accuracy:
1. **The Graph Engine runs FIRST.** All mathematical details (sequence, stops, distance, estimated time, fare, interchange station) are calculated deterministically.
2. **Ground-Truth Prompt Injection:** The calculated facts are injected into a structured system prompt sent to Google Gemini:
   ```
   "Here are the VERIFIED GRAPH FACTS (you MUST NOT alter these):
    Source: Majestic
    Destination: Yeshwanthpur
    Route: Majestic -> Mantri Square -> ... -> Yeshwanthpur
    Stops: 7 | Est. Time: 15 mins | Fare: ₹40
    Explain this route to the commuter with directions and tips."
   ```
3. **Synthesis:** Gemini formats the journey into a polite, easy-to-read narrative with platform advice, safety tips, and fare reminders.
4. **Offline Fallback:** If `GEMINI_API_KEY` is not provided or the network is unreachable, an intelligent rule-based formatter outputs a clear route guide without throwing errors or faking live AI.

---

## 9. Folder Structure

```
metro_project/
│
├── index.html               # Main user interface (HTML5)
├── style.css                # Glassmorphic UI styling (Vanilla CSS)
├── script.js                # Frontend logic & API client (JavaScript)
├── .env.example             # Template for API keys & server settings
├── .gitignore               # Git ignore rules for Python & environments
├── README.md                # Comprehensive project documentation
│
├── backend/
│   ├── app.py               # Flask REST server & static file host
│   ├── metro_data.py        # Station definitions, lines, graph builder
│   ├── route_finder.py      # Dijkstra and BFS shortest-path algorithms
│   ├── ai_assistant.py      # Gemini Generative AI & offline fallback engine
│   ├── test_metro.py        # Automated test suite (unittest)
│   └── requirements.txt     # Python backend dependencies
│
└── screenshots/
    └── README.md            # College submission screenshot capture guide
```

---

## 10. Installation Steps

### Prerequisites
- Python 3.10 or higher installed on your computer.
- A modern web browser (Google Chrome, Firefox, Edge).

### Step 1: Open Terminal in Project Directory
```powershell
cd metro_project
```

### Step 2: (Optional) Create and Activate Virtual Environment
```powershell
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Dependencies
```powershell
pip install -r backend/requirements.txt
```

### Step 4: Configure Gemini API Key (Optional)
If you wish to use live Google Gemini AI generation:
1. Copy `.env.example` to `.env`:
   ```powershell
   copy .env.example .env
   ```
2. Open `.env` and set your key:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```
*(Note: If you do not have an API key, leave it as is. The application automatically runs in Intelligent Offline Assistant mode!)*

---

## 11. How to Run

### Start the Flask Server
```powershell
python backend/app.py
```

You will see:
```
=======================================================
  Bengaluru Metro Route Finder Server Started
  Access web application at: http://127.0.0.1:5000
=======================================================
```

### Open the Web Application
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 12. API Endpoints

| Method | Endpoint | Description | Request Body |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Serves the web frontend (`index.html`) | None |
| `GET` | `/api/health` | Health status and AI configuration check | None |
| `GET` | `/api/stations` | Returns list of all 100+ stations and lines | None |
| `POST` | `/api/find-route` | Calculates optimal route using Dijkstra or BFS | `{"source": "...", "destination": "...", "algorithm": "dijkstra"}` |
| `POST` | `/api/ai-assist` | Generates AI route guide or answers questions | `{"question": "...", "source": "...", "destination": "..."}` |

---

## 13. Sample Input & Output

### Test Case 1: Direct Green Line Travel
- **Source:** `Nadaprabhu Kempegowda Station` (Majestic)
- **Destination:** `Yeshwanthpur`
- **Algorithm:** Dijkstra's Algorithm
- **Output:**
  - **Route:** `Nadaprabhu Kempegowda Station ➔ Mantri Square Sampige Road ➔ Srirampura ➔ Mahakavi Kuvempu Road ➔ Rajajinagar ➔ Mahalakshmi ➔ Sandal Soap Factory ➔ Yeshwanthpur`
  - **Stops:** 7 stations
  - **Estimated Time:** ~15 minutes
  - **Distance:** 9.1 km
  - **Fare:** ₹40
  - **Interchanges:** 0 (Direct)

### Test Case 2: Short Purple Line Travel
- **Source:** `Indiranagar`
- **Destination:** `Mahatma Gandhi Road` (MG Road)
- **Algorithm:** Dijkstra's Algorithm
- **Output:**
  - **Route:** `Indiranagar ➔ Halasuru ➔ Trinity ➔ Mahatma Gandhi Road`
  - **Stops:** 3 stations
  - **Estimated Time:** ~7 minutes
  - **Distance:** 3.9 km
  - **Fare:** ₹20
  - **Interchanges:** 0 (Direct)

### Test Case 3: Line Interchange Journey (Green to Purple Line)
- **Source:** `Jayanagara`
- **Destination:** `Cubbon Park`
- **Algorithm:** Dijkstra's Algorithm
- **Output:**
  - **Route:** `Jayanagara ➔ South End Circle ➔ Lalbagh ➔ National College ➔ Krishna Rajendra Market ➔ Chickpete ➔ Nadaprabhu Kempegowda Station ➔ Sir M. Visvesvaraya Station ➔ Dr. B. R. Ambedkar Station, Vidhana Soudha ➔ Cubbon Park`
  - **Stops:** 9 stations
  - **Estimated Time:** ~25 minutes (includes 5-minute interchange transfer)
  - **Distance:** 11.7 km
  - **Fare:** ₹50
  - **Interchanges:** 1 (`Nadaprabhu Kempegowda Station`: Green Line ➔ Purple Line)

---

## 14. Screenshots Section

Capture the following 5 screens from `http://127.0.0.1:5000` for your college report:

1. **Screenshot 1 – Homepage:** Full view showing title, 4 metro line badges, source/destination dropdowns, algorithm radio toggle, and AI Assistant card.
2. **Screenshot 2 – Station Selection:** Selection of Source (`Nadaprabhu Kempegowda Station`) and Destination (`Yeshwanthpur`).
3. **Screenshot 3 – Calculated Route:** Output displaying the 5 metric pills (Stops, Est. Time, Distance, Fare, Changes) and colored station flow.
4. **Screenshot 4 – AI Metro Assistant Query:** AI input box containing a query like *"Explain my metro route in detail."*.
5. **Screenshot 5 – AI Response Output:** Rendered AI card showing the generated travel explanation and commuter tips.

*(A detailed checklist is provided in [`screenshots/README.md`](screenshots/README.md)).*

---

## 15. Automated Testing

Run the included automated test suite to verify graph algorithms, fare calculations, station normalization, and AI handlers:

```powershell
python backend/test_metro.py
```

Expected output:
```
..........
----------------------------------------------------------------------
Ran 10 tests in 0.001s

OK
```

---

## 16. Future Enhancements

- **Real-Time Train Tracking:** Integration with Namma Metro GPS feeds to display live train arrival times.
- **Crowd Density Estimation:** Predicting peak-hour station crowding using historical transit data.
- **Voice Assistant:** Speech-to-text input in Kannada and English for hands-free navigation.
- **Multimodal Route Planning:** Suggesting BMTC feeder buses and auto-rickshaws for first/last-mile connectivity.

---

## 17. Conclusion

The **Bangalore Metro Route Finder** successfully integrates classical graph theory with state-of-the-art Generative AI. By utilizing **Dijkstra's Algorithm** and **BFS** on a Python Flask backend and constraining the **Google Gemini AI** to deterministic graph data, the application guarantees mathematically accurate routes while offering an intuitive, commuter-friendly conversational interface.
