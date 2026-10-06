"""
app.py
Flask Web Server and RESTful API for Bangalore Metro Route Finder.

Provides endpoints for:
1. Serving static frontend assets (index.html, style.css, script.js)
2. Metro station and network metadata: GET /api/stations
3. Graph-based shortest path route calculation: POST /api/find-route
4. Generative AI commute assistant: POST /api/ai-assist
5. Health and config check: GET /api/health
"""

import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Ensure the backend directory is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Load environment variables (.env in project root or backend folder)
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
load_dotenv(os.path.join(CURRENT_DIR, ".env"))

try:
    from metro_data import (
        get_all_stations,
        normalize_station_name,
        METRO_LINES,
        LINE_COLORS
    )
    from route_finder import MetroRouteFinder
    from ai_assistant import MetroAIAssistant
except ImportError:
    from backend.metro_data import (
        get_all_stations,
        normalize_station_name,
        METRO_LINES,
        LINE_COLORS
    )
    from backend.route_finder import MetroRouteFinder
    from backend.ai_assistant import MetroAIAssistant

app = Flask(__name__, static_folder=PROJECT_ROOT, static_url_path="")
CORS(app)

# Initialize engines
route_finder = MetroRouteFinder()
ai_assistant = MetroAIAssistant()

@app.route("/")
def serve_index():
    """Serves the main application homepage."""
    return send_from_directory(PROJECT_ROOT, "index.html")

@app.route("/favicon.ico")
def favicon():
    """Empty favicon response to prevent 404 in browser console."""
    return "", 204

@app.route("/<path:filename>")
def serve_static_files(filename):
    """Serves styles, scripts, and other assets from project root."""
    if os.path.exists(os.path.join(PROJECT_ROOT, filename)):
        return send_from_directory(PROJECT_ROOT, filename)
    return jsonify({"error": "File not found"}), 404

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify backend status."""
    api_key_configured = bool(os.getenv("GEMINI_API_KEY", "").strip())
    return jsonify({
        "status": "healthy",
        "service": "Bangalore Metro Route Finder Backend",
        "stations_count": len(get_all_stations()),
        "gemini_ai_configured": api_key_configured
    }), 200

@app.route("/api/stations", methods=["GET"])
def list_stations():
    """
    Returns the complete list of Bangalore Metro stations,
    organized lines, and line colors.
    """
    return jsonify({
        "success": True,
        "stations": get_all_stations(),
        "lines": METRO_LINES,
        "line_colors": LINE_COLORS
    }), 200

@app.route("/api/find-route", methods=["POST"])
def find_route():
    """
    Calculates the shortest route using Dijkstra's Algorithm or BFS.
    
    Request JSON:
    {
        "source": "Majestic",
        "destination": "Yeshwanthpur",
        "algorithm": "dijkstra" (optional: "dijkstra" or "bfs")
    }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({
            "success": False,
            "error": "Invalid request. Please provide JSON body with 'source' and 'destination'."
        }), 400

    source = (data.get("source") or "").strip()
    destination = (data.get("destination") or "").strip()
    algorithm = (data.get("algorithm") or "dijkstra").strip().lower()

    # Validation: Empty inputs
    if not source:
        return jsonify({"success": False, "error": "Please select a source station."}), 400
    if not destination:
        return jsonify({"success": False, "error": "Please select a destination station."}), 400

    # Validation: Same station
    norm_src = normalize_station_name(source)
    norm_dst = normalize_station_name(destination)

    if not norm_src:
        return jsonify({"success": False, "error": f"Source station '{source}' is not recognized in the metro network."}), 400
    if not norm_dst:
        return jsonify({"success": False, "error": f"Destination station '{destination}' is not recognized in the metro network."}), 400
    if norm_src == norm_dst:
        return jsonify({"success": False, "error": "Source and destination cannot be the same station."}), 400

    try:
        route_result = route_finder.plan_journey(norm_src, norm_dst, preferred_algo=algorithm)
        response_data = {"success": True, **route_result}
        return jsonify(response_data), 200
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 400
    except RuntimeError as re:
        return jsonify({"success": False, "error": str(re)}), 404
    except Exception as e:
        app.logger.error(f"Unexpected error in find-route: {e}")
        return jsonify({"success": False, "error": "An unexpected error occurred while calculating the route."}), 500

@app.route("/api/ai-assist", methods=["POST"])
def ai_assist():
    """
    Generative AI Assistant endpoint.
    Takes a question and route information, computes explanation using Gemini or rule fallback.
    
    Request JSON:
    {
        "question": "Which station do I change at?",
        "source": "Jayanagar",           (optional if route_data provided)
        "destination": "Cubbon Park",    (optional if route_data provided)
        "route_data": {...}              (optional, previously calculated route)
    }
    """
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    source = (data.get("source") or "").strip()
    destination = (data.get("destination") or "").strip()
    route_data = data.get("route_data")

    if not question and not (source and destination) and not route_data:
        return jsonify({
            "success": False,
            "error": "Please provide a question or select source and destination stations."
        }), 400

    try:
        # If route_data is already provided and matches
        if route_data and isinstance(route_data, dict) and "route" in route_data:
            ai_response = ai_assistant.generate_explanation(route_data, user_question=question)
            return jsonify({"success": True, **ai_response}), 200

        # If source and destination are specified
        if source and destination:
            norm_src = normalize_station_name(source)
            norm_dst = normalize_station_name(destination)
            if not norm_src or not norm_dst or norm_src == norm_dst:
                return jsonify({
                    "success": False,
                    "error": "Please select two distinct and valid metro stations."
                }), 400

            calculated = route_finder.plan_journey(norm_src, norm_dst)
            ai_response = ai_assistant.generate_explanation(calculated, user_question=question)
            ai_response["calculated_route"] = calculated
            return jsonify({"success": True, **ai_response}), 200

        # If question contains stations in natural language
        if question:
            ai_response = ai_assistant.answer_query(question, current_source=source or None, current_dest=destination or None)
            if "error" in ai_response and not ai_response.get("explanation"):
                return jsonify({"success": False, "error": ai_response["error"]}), 400
            return jsonify({"success": True, **ai_response}), 200

        return jsonify({"success": False, "error": "Insufficient details to answer query."}), 400

    except Exception as e:
        app.logger.error(f"Unexpected error in ai-assist: {e}")
        return jsonify({
            "success": False,
            "error": "An unexpected error occurred while generating the AI response."
        }), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() in ["true", "1", "yes"]
    print(f"\n=======================================================")
    print(f"  Bengaluru Metro Route Finder Server Started")
    print(f"  Access web application at: http://127.0.0.1:{port}")
    print(f"=======================================================\n")
    app.run(host="127.0.0.1", port=port, debug=debug)
