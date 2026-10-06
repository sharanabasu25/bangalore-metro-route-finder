/**
 * script.js
 * Bangalore Metro Route Finder Frontend Logic
 * Integrates directly with the Python Flask Backend (Dijkstra, BFS, Gemini AI).
 */

document.addEventListener("DOMContentLoaded", function () {
  const srcSelect = document.getElementById("src");
  const dstSelect = document.getElementById("dst");
  const resultsEl = document.getElementById("results");
  const aiInput = document.getElementById("aiInput");
  const aiResponse = document.getElementById("aiResponse");
  const aiStatusBadge = document.getElementById("aiStatusBadge");

  // Global cache of latest route for seamless AI interaction
  let currentCalculatedRoute = null;

  // Determine API Base URL dynamically
  // Supports both direct Flask serving (relative) and Live Server / file viewing
  const API_BASE = (window.location.protocol === "file:" || !window.location.port)
    ? "http://127.0.0.1:5000"
    : "";

  // Complete offline station fallback list in case backend is starting up
  const fallbackStations = [
    "Attiguppe", "BTM Layout", "Baiyappanahalli", "Banashankari", "Benniganahalli",
    "Beratena Agrahara", "Biocon", "Bommanahalli", "Bommasandra", "Cantonment",
    "Central Silk Board", "Challaghatta", "Chickpete", "Chikkabidarakallu", "Cubbon Park",
    "Dairy Circle", "Dasarahalli", "Delta Electronics", "Doddakallasandra",
    "Dr. B. R. Ambedkar Station, Vidhana Soudha", "Electronic City", "Garudacharpalya",
    "Goragunte Palya", "Halasuru", "Hebbagodi", "Hongasandra", "Hoodi", "Hopefarm Channasandra",
    "Hosa Road", "Hulimavu", "Huskur Road", "IIMB", "Indiranagar", "JP Nagar 4th Phase",
    "Jalahalli", "Jaya Prakash Nagar", "Jayadeva Hospital", "Jayanagara", "Jnanabharathi",
    "KR Pura", "Kadugodi Tree Park", "Kadugundanahalli", "Kalena Agrahara", "Kengeri",
    "Kengeri Bus Terminal", "Konakkunte Cross", "Konappana Agrahara",
    "Krantivira Sangolli Rayanna Railway Station", "Krishna Rajendra Market", "Kudlu Gate",
    "Kundalahalli", "Lakkasandra", "Lalbagh", "Langford Town", "Madavara", "Magadi Road",
    "Mahakavi Kuvempu Road", "Mahalakshmi", "Mahatma Gandhi Road", "Manjunatha Nagara",
    "Mantri Square Sampige Road", "Mysuru Road", "Nadaprabhu Kempegowda Station",
    "Nagasandra", "Nallurhalli", "National College", "National Military School",
    "Pantharapalya - Nayandahalli", "Pattandur Agrahara", "Pattanagere", "Peenya",
    "Peenya Industry", "Pottery Town", "Ragigudda", "Rajarajeshwari Nagar", "Rajajinagar",
    "Rashtreeya Vidyalaya Road", "Sandal Soap Factory", "Seetharamapalya", "Shivajinagar",
    "Silk Institute", "Singasandra", "Singayyanapalya", "Sir M. Visvesvaraya Station",
    "South End Circle", "Sri Balagangadharanatha Swamiji Station, Hosahalli",
    "Sri Sathya Sai Hospital", "Srirampura", "Swami Vivekananda Road", "Tannery Road",
    "Tavarekere", "Thalaghattapura", "Trinity", "Vajarahalli", "Venkateshpura",
    "Vijayanagar", "Whitefield", "Yelachenahalli", "Yeshwanthpur"
  ];

  // 1. Initialize station options
  function populateDropdowns(stations) {
    srcSelect.innerHTML = '<option value="">Select Source Station</option>';
    dstSelect.innerHTML = '<option value="">Select Destination Station</option>';

    stations.forEach(st => {
      const opt1 = document.createElement("option");
      opt1.value = st;
      opt1.textContent = st;
      srcSelect.appendChild(opt1);

      const opt2 = document.createElement("option");
      opt2.value = st;
      opt2.textContent = st;
      dstSelect.appendChild(opt2);
    });
  }

  // Fetch stations from Python backend
  fetch(`${API_BASE}/api/stations`)
    .then(res => res.json())
    .then(data => {
      if (data.stations && data.stations.length) {
        populateDropdowns(data.stations);
      } else {
        populateDropdowns(fallbackStations);
      }
    })
    .catch(err => {
      console.warn("Backend not yet reached, using local station list:", err);
      populateDropdowns(fallbackStations);
    });

  // Check health and AI status
  fetch(`${API_BASE}/api/health`)
    .then(res => res.json())
    .then(data => {
      if (aiStatusBadge) {
        if (data.gemini_ai_configured) {
          aiStatusBadge.textContent = "Gemini Live AI";
          aiStatusBadge.style.color = "#4ade80";
        } else {
          aiStatusBadge.textContent = "Offline Smart Assistant";
          aiStatusBadge.style.color = "#facc15";
        }
      }
    })
    .catch(() => {});

  // 2. Swap Stations Helper
  window.swapStations = function () {
    const temp = srcSelect.value;
    srcSelect.value = dstSelect.value;
    dstSelect.value = temp;

    if (srcSelect.value && dstSelect.value) {
      window.findRoutes();
    }
  };

  // 3. Set AI Prompt from chips
  window.setAiPrompt = function (text) {
    if (aiInput) {
      aiInput.value = text;
      window.askAI();
    }
  };

  // Simple Markdown to Safe HTML renderer for AI output
  function renderMarkdown(md) {
    if (!md) return "";
    let html = md
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");

    // Headers
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h3>$1</h3>');

    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

    // Bullet points
    html = html.replace(/^\s*• (.*$)/gim, '<li>$1</li>');
    html = html.replace(/^\s*\* (.*$)/gim, '<li>$1</li>');
    html = html.replace(/^\s*- (.*$)/gim, '<li>$1</li>');

    // Wrap consecutive <li> into <ul>
    html = html.replace(/(<li>[\s\S]*?<\/li>)/g, '<ul>$1</ul>');
    html = html.replace(/<\/ul>\s*<ul>/g, '');

    // Paragraph breaks
    html = html.replace(/\n{2,}/g, '</p><p>');
    html = html.replace(/\n/g, '<br>');
    return `<div class="ai-response-content"><p>${html}</p></div>`;
  }

  // 4. Main Route Finding Function (Calls Python Flask Backend)
  window.findRoutes = function () {
    const s = srcSelect.value;
    const d = dstSelect.value;
    const algoInput = document.querySelector('input[name="algorithm"]:checked');
    const algorithm = algoInput ? algoInput.value : "dijkstra";

    if (!s || !d) {
      resultsEl.innerHTML = "<p class='msg'>Please select both source and destination stations.</p>";
      return;
    }

    if (s === d) {
      resultsEl.innerHTML = "<p class='msg error'>Source and destination cannot be the same station.</p>";
      return;
    }

    const btn = document.getElementById("findRouteBtn");
    if (btn) {
      btn.disabled = true;
      btn.innerHTML = '<span class="spinner"></span> Calculating Shortest Path...';
    }

    resultsEl.innerHTML = '<p class="msg"><span class="spinner"></span> Running Python Graph Algorithm...</p>';

    fetch(`${API_BASE}/api/find-route`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        source: s,
        destination: d,
        algorithm: algorithm
      })
    })
      .then(async (res) => {
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.error || "Route calculation failed.");
        }
        return data;
      })
      .then((data) => {
        currentCalculatedRoute = data;
        renderRouteResult(data);

        // Pre-fill a helpful placeholder in AI Assistant
        if (aiInput && !aiInput.value) {
          aiInput.placeholder = `Ask AI about your trip from ${data.source} to ${data.destination}...`;
        }
      })
      .catch((err) => {
        resultsEl.innerHTML = `<p class='msg error'>${err.message || "Failed to connect to Python backend."}</p>`;
      })
      .finally(() => {
        if (btn) {
          btn.disabled = false;
          btn.textContent = "Find Routes";
        }
      });
  };

  // 5. Render Calculated Route Result
  function renderRouteResult(data) {
    const {
      source,
      destination,
      route,
      stations,
      estimated_time,
      distance,
      fare,
      interchanges,
      algorithm,
      path_details
    } = data;

    // Build flow of stations
    const flowHtml = path_details.map((item, idx) => {
      let extraClass = "";
      if (item.is_start) extraClass = "origin";
      else if (item.is_end) extraClass = "dest";
      else if (item.is_interchange) extraClass = "interchange";

      const arrow = idx < path_details.length - 1 ? '<span class="st-arrow">➔</span>' : '';
      const borderStyle = `border-left: 4px solid ${item.color || '#8b5cf6'};`;

      return `<span class="st ${extraClass}" style="${borderStyle}">
        ${item.station}
      </span> ${arrow}`;
    }).join(" ");

    // Interchange Alert box if applicable
    let interchangeNotice = "";
    if (interchanges && interchanges.length > 0) {
      const changeList = interchanges.map(c => 
        `Switch at <strong>${c.station}</strong> from <strong>${c.from_line} Line</strong> to <strong>${c.to_line} Line</strong>`
      ).join("; ");
      interchangeNotice = `
        <div class="interchange-box">
          🔄 <strong>Interchange Required:</strong> ${changeList}
        </div>
      `;
    }

    const html = `
      <div class="route-card">
        <div class="route-header">
          <div class="route-title">
            <span>🚇 Optimal Journey Plan</span>
          </div>
          <span class="route-algo-tag">${algorithm}</span>
        </div>

        <div class="stats-grid">
          <div class="stat-pill">
            <div class="stat-value">${stations}</div>
            <div class="stat-label">Stops</div>
          </div>
          <div class="stat-pill">
            <div class="stat-value">~${estimated_time} m</div>
            <div class="stat-label">Est. Time</div>
          </div>
          <div class="stat-pill">
            <div class="stat-value">${distance} km</div>
            <div class="stat-label">Distance</div>
          </div>
          <div class="stat-pill">
            <div class="stat-value">₹${fare}</div>
            <div class="stat-label">Metro Fare</div>
          </div>
          <div class="stat-pill">
            <div class="stat-value">${interchanges ? interchanges.length : 0}</div>
            <div class="stat-label">Line Changes</div>
          </div>
        </div>

        ${interchangeNotice}

        <div class="station-flow-wrap">
          <div class="station-flow-label">Step-by-Step Station Sequence:</div>
          <div class="station-flow">
            ${flowHtml}
          </div>
        </div>
      </div>
    `;

    resultsEl.innerHTML = html;
  }

  // 6. Generative AI Metro Assistant Integration
  window.askAI = function () {
    const question = aiInput.value.trim();
    const askBtn = document.getElementById("askAiBtn");

    if (!question && !currentCalculatedRoute && (!srcSelect.value || !dstSelect.value)) {
      aiResponse.style.display = "block";
      aiResponse.innerHTML = "<p class='msg'>Please enter a question or select a route first.</p>";
      return;
    }

    aiResponse.style.display = "block";
    aiResponse.innerHTML = '<span class="spinner"></span> Thinking... Synthesizing route guidance with Generative AI...';

    if (askBtn) {
      askBtn.disabled = true;
    }

    const payload = {
      question: question || "Explain my metro route in detail.",
      source: srcSelect.value || (currentCalculatedRoute ? currentCalculatedRoute.source : null),
      destination: dstSelect.value || (currentCalculatedRoute ? currentCalculatedRoute.destination : null),
      route_data: currentCalculatedRoute
    };

    fetch(`${API_BASE}/api/ai-assist`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    })
      .then(async (res) => {
        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.error || "AI Assistant could not respond.");
        }
        return data;
      })
      .then((data) => {
        const providerName = data.provider || "AI Metro Assistant";
        const isLive = data.is_live_ai;
        const badgeColor = isLive ? "background: rgba(34, 197, 94, 0.2); color: #4ade80;" : "background: rgba(250, 204, 21, 0.2); color: #facc15;";

        const formattedBody = renderMarkdown(data.explanation);

        // If the query calculated a new route in the process, update the UI
        if (data.calculated_route && (!currentCalculatedRoute || currentCalculatedRoute.source !== data.calculated_route.source)) {
          currentCalculatedRoute = data.calculated_route;
          srcSelect.value = data.calculated_route.source;
          dstSelect.value = data.calculated_route.destination;
          renderRouteResult(data.calculated_route);
        }

        aiResponse.innerHTML = `
          <div class="ai-response-meta">
            <span><strong>Namma Metro AI Assistant</strong></span>
            <span class="ai-provider-badge" style="${badgeColor}">${providerName}</span>
          </div>
          ${formattedBody}
        `;
      })
      .catch((err) => {
        aiResponse.innerHTML = `<p class='msg error'>AI Assistant Error: ${err.message || "Failed to generate explanation."}</p>`;
      })
      .finally(() => {
        if (askBtn) {
          askBtn.disabled = false;
        }
      });
  };
});