document.addEventListener("DOMContentLoaded", function () {

  const graph = {};

  function addConn(a, b, line) {
    graph[a] = graph[a] || [];
    graph[b] = graph[b] || [];
    graph[a].push({ to: b, line });
    graph[b].push({ to: a, line });
  }

  
  const lineColors = {
    "Purple": "#a855f7",
    "Green": "#22c55e",
    "Yellow": "#facc15",
    "Pink": "#ec4899"
  };

  function getLine(a, b) {
    const conn = (graph[a] || []).find(x => x.to === b);
    return conn ? conn.line : "Purple";
  }



  const purple = [
    "Challaghatta","Kengeri","Kengeri Bus Terminal","Pattanagere","Jnanabharathi",
    "Rajarajeshwari Nagar","Pantharapalya - Nayandahalli","Mysuru Road",
    "Deepanjali Nagar","Attiguppe","Vijayanagar",
    "Sri Balagangadharanatha Swamiji Station, Hosahalli","Magadi Road",
    "Krantivira Sangolli Rayanna Railway Station",
    "Nadaprabhu Kempegowda Station","Sir M. Visvesvaraya Station",
    "Dr. B. R. Ambedkar Station, Vidhana Soudha",
    "Cubbon Park","Mahatma Gandhi Road","Trinity","Halasuru",
    "Indiranagar","Swami Vivekananda Road","Baiyappanahalli",
    "Benniganahalli","KR Pura","Singayyanapalya","Garudacharpalya",
    "Hoodi","Seetharamapalya","Kundalahalli","Nallurhalli",
    "Sri Sathya Sai Hospital","Pattandur Agrahara",
    "Kadugodi Tree Park","Hopefarm Channasandra","Whitefield"
  ];

  const green = [
    "Madavara","Chikkabidarakallu","Manjunatha Nagara","Nagasandra",
    "Dasarahalli","Jalahalli","Peenya Industry","Peenya",
    "Goragunte Palya","Yeshwanthpur","Sandal Soap Factory",
    "Mahalakshmi","Rajajinagar","Mahakavi Kuvempu Road",
    "Srirampura","Mantri Square Sampige Road",
    "Nadaprabhu Kempegowda Station",
    "Chickpete","Krishna Rajendra Market","National College",
    "Lalbagh","South End Circle","Jayanagara",
    "Rashtreeya Vidyalaya Road","Banashankari",
    "Jaya Prakash Nagar","Yelachenahalli","Konanakunte Cross",
    "Doddakallasandra","Vajarahalli","Thalaghattapura","Silk Institute"
  ];

  const yellow = [
    "Rashtreeya Vidyalaya Road","Ragigudda","Jayadeva Hospital",
    "BTM Layout","Central Silk Board","Bommanahalli",
    "Hongasandra","Kudlu Gate","Singasandra","Hosa Road",
    "Beratena Agrahara","Electronic City","Infosys Foundation",
    "Konappana Agrahara","Huskur Road","Biocon",
    "Hebbagodi","Delta Electronics","Bommasandra"
  ];

  const pink = [
    "Kalena Agrahara","Hulimavu","IIMB","JP Nagar 4th Phase",
    "Jayadeva Hospital","Tavarekere","Dairy Circle","Lakkasandra",
    "Langford Town","National Military School","Mahatma Gandhi Road",
    "Shivajinagar","Cantonment","Pottery Town","Tannery Road",
    "Venkateshpura","Kadugundanahalli","Nagawara"
  ];


  [["Purple",purple],["Green",green],["Yellow",yellow],["Pink",pink]]
  .forEach(([line, stations]) => {
    for (let i = 0; i < stations.length - 1; i++) {
      addConn(stations[i], stations[i + 1], line);
    }
  });


  const src = document.getElementById("src");
  const dst = document.getElementById("dst");

  const allStations = [...new Set([
    ...purple, ...green, ...yellow, ...pink
  ])].sort();

  allStations.forEach(st => {
    src.innerHTML += `<option value="${st}">${st}</option>`;
    dst.innerHTML += `<option value="${st}">${st}</option>`;
  });


  function findMultipleRoutes(start, end, maxRoutes = 5) {
    const queue = [[start]];
    const routes = [];

    while (queue.length && routes.length < maxRoutes) {
      const path = queue.shift();
      const node = path[path.length - 1];

      if (node === end) {
        routes.push(path);
        continue;
      }

      for (const { to } of graph[node] || []) {
        if (!path.includes(to)) {
          queue.push([...path, to]);
        }
      }
    }

    return routes;
  }


  function getInterchanges(route) {
    let prevLine = null;
    const changes = [];

    for (let i = 0; i < route.length - 1; i++) {
      const seg = (graph[route[i]] || []).find(x => x.to === route[i+1]);
      if (!seg) continue;

      if (prevLine && prevLine !== seg.line) {
        changes.push({
          station: route[i],
          from: prevLine,
          to: seg.line
        });
      }

      prevLine = seg.line;
    }

    return changes;
  }


  function fare(stops) {
    if (stops <= 2) return 10;
    if (stops <= 4) return 20;
    if (stops <= 6) return 30;
    if (stops <= 8) return 40;
    if (stops <= 10) return 50;
    if (stops <= 16) return 60;
    if (stops <= 18) return 70;
    if (stops <= 26) return 80;
    return 90;
  }


  window.findRoutes = function () {
    const s = src.value;
    const d = dst.value;
    const el = document.getElementById("results");

    if (!s || !d) {
      el.innerHTML = "<p class='msg'>Select stations</p>";
      return;
    }

    if (s === d) {
      el.innerHTML = "<p class='msg'>Same station selected</p>";
      return;
    }

    const routes = findMultipleRoutes(s, d, 2);

    if (!routes.length) {
      el.innerHTML = "<p class='msg'>No route found</p>";
      return;
    }

    routes.sort((a, b) => a.length - b.length);

    let html = "";

    routes.forEach((route, i) => {
      const stops = route.length - 1;
      const cost = fare(stops);
      const changes = getInterchanges(route);

      
      const coloredRoute = route.map((st, idx) => {

        let prevLine = null;
        let nextLine = null;

        if (idx > 0) prevLine = getLine(route[idx - 1], st);
        if (idx < route.length - 1) nextLine = getLine(st, route[idx + 1]);

        if (prevLine && nextLine && prevLine !== nextLine) {
          return `<span class="st" style="
            background: linear-gradient(90deg,
              ${lineColors[prevLine]} 50%,
              ${lineColors[nextLine]} 50%);
            color:black;
            font-weight:600;
          ">
            ${st}
          </span>`;
        }

        return `<span class="st">${st}</span>`;
      }).join(" → ");

      html += `
      <div class="route-card">
        <b>${i === 0 ? " Best Route" : "Route " + (i+1)}</b><br>
        Stations: ${stops} | Fare: ₹${cost} | Changes: ${changes.length}<br><br>

        ${coloredRoute}

        ${changes.length ? `
          <div style="margin-top:8px;">
            Change at:
            ${changes.map(c => `<b>${c.station}</b> (${c.from} → ${c.to})`).join(", ")}
          </div>
        ` : ""}
      </div>`;
    });

    el.innerHTML = html;
  };

});
maxRoutes