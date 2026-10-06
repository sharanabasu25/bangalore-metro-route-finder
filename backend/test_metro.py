"""
test_metro.py
Automated verification tests for Bangalore Metro Route Finder.
Tests Graph algorithms (Dijkstra, BFS), data integrity, and AI assistant.
"""

import unittest
from metro_data import get_all_stations, METRO_LINES, normalize_station_name
from route_finder import MetroRouteFinder, calculate_fare
from ai_assistant import MetroAIAssistant

class TestBangaloreMetro(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.finder = MetroRouteFinder()
        cls.ai = MetroAIAssistant()

    def test_01_station_data_integrity(self):
        """Verify all 4 metro lines are loaded and stations are present."""
        stations = get_all_stations()
        self.assertGreater(len(stations), 90, "Should have all Namma Metro stations")
        self.assertIn("Purple", METRO_LINES)
        self.assertIn("Green", METRO_LINES)
        self.assertIn("Yellow", METRO_LINES)
        self.assertIn("Pink", METRO_LINES)

    def test_02_station_alias_normalization(self):
        """Verify colloquial Bangalore station names map to canonical stations."""
        self.assertEqual(normalize_station_name("Majestic"), "Nadaprabhu Kempegowda Station")
        self.assertEqual(normalize_station_name("MG Road"), "Mahatma Gandhi Road")
        self.assertEqual(normalize_station_name("RV Road"), "Rashtreeya Vidyalaya Road")

    def test_03_dijkstra_testcase_1_majestic_to_yeshwanthpur(self):
        """Test Case 1: Majestic to Yeshwanthpur."""
        res = self.finder.plan_journey("Majestic", "Yeshwanthpur", preferred_algo="dijkstra")
        self.assertEqual(res["source"], "Nadaprabhu Kempegowda Station")
        self.assertEqual(res["destination"], "Yeshwanthpur")
        self.assertEqual(res["stations"], 7)
        self.assertIn("Mantri Square Sampige Road", res["route"])
        self.assertIn("Srirampura", res["route"])
        self.assertIn("Mahakavi Kuvempu Road", res["route"])
        self.assertIn("Rajajinagar", res["route"])
        self.assertIn("Mahalakshmi", res["route"])
        self.assertGreater(res["distance"], 8.0)
        self.assertGreater(res["estimated_time"], 10)

    def test_04_testcase_2_indiranagar_to_mg_road(self):
        """Test Case 2: Indiranagar to MG Road (Direct Purple Line)."""
        res = self.finder.plan_journey("Indiranagar", "MG Road")
        self.assertEqual(res["stations"], 3)
        self.assertEqual(res["interchanges_count"], 0)
        self.assertEqual(res["fare"], 20)

    def test_05_testcase_3_jayanagar_to_cubbon_park(self):
        """Test Case 3: Jayanagar to Cubbon Park (Interchange at Majestic)."""
        res = self.finder.plan_journey("Jayanagar", "Cubbon Park")
        self.assertEqual(res["interchanges_count"], 1)
        self.assertEqual(res["interchanges"][0]["station"], "Nadaprabhu Kempegowda Station")
        self.assertEqual(res["interchanges"][0]["from_line"], "Green")
        self.assertEqual(res["interchanges"][0]["to_line"], "Purple")

    def test_06_bfs_algorithm(self):
        """Verify BFS returns shortest path in terms of station stops."""
        res = self.finder.plan_journey("Indiranagar", "MG Road", preferred_algo="bfs")
        self.assertEqual(res["stations"], 3)
        self.assertIn("BFS", res["algorithm"])

    def test_07_validation_same_station(self):
        """Verify same station throws ValueError."""
        with self.assertRaises(ValueError):
            self.finder.plan_journey("Indiranagar", "Indiranagar")

    def test_08_validation_invalid_station(self):
        """Verify invalid station throws ValueError."""
        with self.assertRaises(ValueError):
            self.finder.plan_journey("Hogwarts Express", "Indiranagar")

    def test_09_fare_calculation(self):
        """Verify official fare slabs."""
        self.assertEqual(calculate_fare(1), 10)
        self.assertEqual(calculate_fare(2), 10)
        self.assertEqual(calculate_fare(4), 20)
        self.assertEqual(calculate_fare(6), 30)
        self.assertEqual(calculate_fare(10), 50)
        self.assertEqual(calculate_fare(16), 60)

    def test_10_ai_assistant_explanation(self):
        """Verify AI assistant generates structured explanation without errors."""
        res = self.ai.answer_query("How to go from Indiranagar to MG Road?")
        self.assertIn("explanation", res)
        self.assertIn("Indiranagar", res["explanation"])
        self.assertIn("Mahatma Gandhi Road", res["explanation"])

if __name__ == "__main__":
    unittest.main()
