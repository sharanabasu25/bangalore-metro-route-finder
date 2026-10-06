"""
ai_assistant.py
Generative AI Route Explainer and Metro Assistant for Bangalore Metro.

Architecture & Grounding:
1. The route is strictly computed by the Python Graph Algorithm (Dijkstra/BFS) FIRST.
2. The calculated facts (stations, stops, distance, time, fare, interchanges)
   are passed to the AI model as ground truth.
3. The AI synthesizes a human-friendly, commuter-oriented explanation
   without hallucinating or altering the graph path.
4. Fallback mechanism: If GEMINI_API_KEY is not set or network is unreachable,
   an intelligent rule-based route breakdown is provided with clear attribution.
"""

import os
import re
from typing import Dict, Any, Optional, Tuple
import requests
from dotenv import load_dotenv

# Load local environment variables from .env if present
load_dotenv()

try:
    from backend.metro_data import get_all_stations, normalize_station_name
    from backend.route_finder import MetroRouteFinder
except ImportError:
    from metro_data import get_all_stations, normalize_station_name
    from route_finder import MetroRouteFinder

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
GEMINI_ENDPOINT = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

class MetroAIAssistant:
    """
    Intelligent AI Assistant that explains calculated metro journeys
    and answers commuter questions.
    """

    def __init__(self):
        self.route_finder = MetroRouteFinder()
        self.all_stations = get_all_stations()

    def parse_stations_from_text(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extracts source and destination station names from natural language queries.
        e.g., 'How do I go from Indiranagar to MG Road?' -> ('Indiranagar', 'Mahatma Gandhi Road')
        """
        lower = text.lower()
        
        # Regex patterns: "from X to Y", "X to Y", "between X and Y"
        patterns = [
            r'from\s+([a-zA-Z0-9\s,\.-]+?)\s+to\s+([a-zA-Z0-9\s,\.-]+)',
            r'between\s+([a-zA-Z0-9\s,\.-]+?)\s+and\s+([a-zA-Z0-9\s,\.-]+)',
            r'([a-zA-Z0-9\s,\.-]+?)\s+to\s+([a-zA-Z0-9\s,\.-]+)'
        ]

        for pat in patterns:
            match = re.search(pat, lower)
            if match:
                raw_src = match.group(1).strip()
                raw_dst = match.group(2).strip()
                
                # Strip trailing punctuation or filler words
                raw_src = re.sub(r'^(travel|take|go|reach|route|navigate)\s+', '', raw_src)
                raw_dst = re.sub(r'\?|\.|\!|\s+(please|fast|today)$', '', raw_dst)

                src = normalize_station_name(raw_src)
                dst = normalize_station_name(raw_dst)
                if src and dst and src != dst:
                    return src, dst

        return None, None

    def generate_explanation(self, route_data: Dict[str, Any], user_question: Optional[str] = None) -> Dict[str, Any]:
        """
        Takes the calculated route data from the graph engine and generates
        a commuter-friendly explanation using Gemini AI or structured fallback.
        """
        source = route_data["source"]
        destination = route_data["destination"]
        route = route_data["route"]
        stations_count = route_data["stations"]
        time_est = route_data["estimated_time"]
        distance = route_data["distance"]
        fare = route_data["fare"]
        interchanges = route_data.get("interchanges", [])
        question = user_question or f"Explain the best metro route from {source} to {destination}."

        # Check if Gemini API key is available
        api_key = os.getenv("GEMINI_API_KEY", "").strip() or GEMINI_API_KEY
        if api_key and api_key != "your_api_key_here":
            try:
                ai_text = self._call_gemini_api(api_key, route_data, question)
                return {
                    "source": source,
                    "destination": destination,
                    "provider": "Google Gemini Generative AI",
                    "model": GEMINI_MODEL,
                    "is_live_ai": True,
                    "explanation": ai_text
                }
            except Exception as e:
                # Log on server console and fallback gracefully
                print(f"[AI Assistant Warning] Gemini API call failed: {e}. Falling back to structured engine.")

        # Fallback structured explanation
        fallback_text = self._generate_fallback_explanation(route_data, question)
        return {
            "source": source,
            "destination": destination,
            "provider": "Intelligent Rule-Based Assistant (Offline Mode)",
            "model": "Deterministic Graph Summarizer",
            "is_live_ai": False,
            "note": "To enable dynamic live Gemini Generative AI, set GEMINI_API_KEY in backend/.env",
            "explanation": fallback_text
        }

    def _call_gemini_api(self, api_key: str, route_data: Dict[str, Any], user_question: str) -> str:
        """Calls Google Gemini API with strict grounding on graph facts."""
        interchange_str = "None (Direct Journey)"
        if route_data.get("interchanges"):
            interchange_str = ", ".join([
                f"Change at {c['station']} from {c['from_line']} Line to {c['to_line']} Line"
                for c in route_data["interchanges"]
            ])

        prompt = f"""
You are the official 'Namma Metro AI Assistant' for the Bengaluru Metro network.
A commuter is asking: "{user_question}"

The route has already been calculated with 100% accuracy using a shortest-path graph algorithm.
Here are the VERIFIED GRAPH FACTS (you MUST NOT alter or hallucinate these facts):
- Source Station: {route_data['source']}
- Destination Station: {route_data['destination']}
- Route Sequence: {' -> '.join(route_data['route'])}
- Total Stops: {route_data['stations']}
- Estimated Travel Time: {route_data['estimated_time']} minutes
- Total Distance: {route_data['distance']} km
- Approximate Fare: ₹{route_data['fare']}
- Line Interchanges: {interchange_str}

YOUR TASK:
Provide a concise, polite, commuter-friendly explanation formatted in clean markdown:
1. Journey Overview: Boarding line and heading.
2. Step-by-Step Directions: Explain the path clearly. Mention where to switch lines if an interchange is required.
3. Travel Stats: Time, distance, and fare.
4. Bangalore Commuter Tip: One quick practical tip (e.g., peak hour travel, QR tickets, AFC gates, card balance).

Keep it professional, helpful, and concise (under 200 words).
"""

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 500
            }
        }

        url = f"{GEMINI_ENDPOINT}?key={api_key}"
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code != 200:
            raise RuntimeError(f"Gemini API returned status {response.status_code}: {response.text}")

        data = response.json()
        candidates = data.get("candidates", [])
        if not candidates:
            raise RuntimeError("Gemini returned empty candidates.")

        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            raise RuntimeError("Gemini response missing content parts.")

        return parts[0].get("text", "").strip()

    def _generate_fallback_explanation(self, route_data: Dict[str, Any], user_question: str) -> str:
        """
        Produces an intelligent, structured response when live API key is unavailable.
        Uses exact graph metrics so facts are 100% accurate.
        """
        source = route_data["source"]
        destination = route_data["destination"]
        stops = route_data["stations"]
        time_est = route_data["estimated_time"]
        distance = route_data["distance"]
        fare = route_data["fare"]
        interchanges = route_data.get("interchanges", [])
        route = route_data["route"]
        first_segment = route_data.get("path_details", [{}])[0].get("line", "Metro")

        lines_used = list(set([p.get("line") for p in route_data.get("path_details", []) if p.get("line")]))
        lines_str = " & ".join(lines_used) if lines_used else "Namma Metro"

        explanation_lines = [
            f"### 🚇 Route Guide: **{source}** ➔ **{destination}**",
            "",
            f"• **Lines:** {lines_str}",
            f"• **Stops:** {stops} stations | **Est. Time:** ~{time_est} mins | **Distance:** {distance} km",
            f"• **Estimated Fare:** ₹{fare} (Smart Card / WhatsApp & Namma Metro QR)",
            ""
        ]

        if not interchanges:
            explanation_lines.extend([
                f"✅ **Direct Journey (No Transfer Needed):**",
                f"Board the **{first_segment} Line** train at **{source}** towards **{destination}**.",
                f"Stay on the train for **{stops} stops** and alight directly at **{destination}**."
            ])
        else:
            explanation_lines.append("🔄 **Transfer Instructions:**")
            explanation_lines.append(f"1. Board the **{interchanges[0]['from_line']} Line** at **{source}**.")
            for idx, chg in enumerate(interchanges, start=1):
                explanation_lines.append(
                    f"{idx + 1}. Alight at **{chg['station']}** and follow directional signage to switch to the **{chg['to_line']} Line** platform."
                )
            explanation_lines.append(f"{len(interchanges) + 2}. Continue on the train to your final stop at **{destination}**.")

        explanation_lines.extend([
            "",
            "💡 **Commuter Tip:**",
            "Metro trains in Bengaluru run with a 5-10 minute frequency during peak hours (8:30 AM – 10:30 AM and 5:30 PM – 8:00 PM). Ensure your Namma Metro card has at least ₹50 balance or scan your QR code at the AFC gate."
        ])

        return "\n".join(explanation_lines)

    def answer_query(self, user_question: str, current_source: Optional[str] = None, current_dest: Optional[str] = None) -> Dict[str, Any]:
        """
        Comprehensive query handler:
        - If query mentions stations, extracts them and runs graph calculation.
        - Otherwise, uses currently selected route.
        """
        extracted_src, extracted_dst = self.parse_stations_from_text(user_question)
        
        src = extracted_src or current_source
        dst = extracted_dst or current_dest

        if not src or not dst:
            return {
                "error": "Could not identify source and destination stations. Please select both stations or mention them (e.g., 'From Indiranagar to MG Road').",
                "explanation": "Please select a source and destination station above, or ask a question like 'How do I travel from Indiranagar to MG Road?'."
            }

        try:
            route_data = self.route_finder.plan_journey(src, dst)
            result = self.generate_explanation(route_data, user_question)
            result["calculated_route"] = route_data
            return result
        except Exception as e:
            return {
                "error": str(e),
                "explanation": f"Sorry, could not calculate route between '{src}' and '{dst}': {str(e)}"
            }
