# Screenshot Guide for College Submission

Capture the following 5 screenshots from `http://127.0.0.1:5000`:

### Screenshot 1: Homepage
- **URL**: `http://127.0.0.1:5000/`
- **What to show**: The initial landing screen showing the header, line badges (Purple, Green, Yellow, Pink), station selectors, algorithm options (Dijkstra / BFS), and the AI Metro Assistant card.

### Screenshot 2: Source and Destination Selected
- **Action**: Select **"Nadaprabhu Kempegowda Station"** (Majestic) in the Boarding Station dropdown, and **"Yeshwanthpur"** in the Alighting Station dropdown.
- **What to show**: The card with both dropdowns selected before clicking "Find Routes".

### Screenshot 3: Calculated Route Output
- **Action**: Click the **"Find Routes"** button.
- **What to show**: The generated route card showing:
  - Metrics: **Stops (7)**, **Est. Time (~15 m)**, **Distance (9.1 km)**, **Fare (₹40)**, **Line Changes (0)**.
  - Station sequence flow: `Nadaprabhu Kempegowda Station ➔ Mantri Square Sampige Road ➔ Srirampura ➔ Mahakavi Kuvempu Road ➔ Rajajinagar ➔ Mahalakshmi ➔ Sandal Soap Factory ➔ Yeshwanthpur`.

### Screenshot 4: AI Metro Assistant Question
- **Action**: In the AI Metro Assistant card, click the prompt chip **"Explain my route"** or type a query like:
  `"How do I travel from Indiranagar to MG Road?"`
- **What to show**: The input field with the user's question before clicking "Ask AI".

### Screenshot 5: AI-Generated Route Explanation
- **Action**: Click **"Ask AI"**.
- **What to show**: The generated response box displaying:
  - AI Provider badge (Google Gemini Generative AI or Intelligent Offline Smart Assistant)
  - Detailed route guide with boarding instructions, line transfers, duration, and local Bangalore commuter tips.
