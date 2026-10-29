(() => {
  "use strict";

  const origin = [53.3498, -6.2603];
  const map = L.map("map", { zoomControl: false }).setView(origin, 13);
  L.control.zoom({ position: "bottomright" }).addTo(map);

  L.tileLayer("https://tile.openstreetmap.de/{z}/{x}/{y}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a> · Tiles by <a href="https://www.openstreetmap.de/">FOSSGIS / OpenStreetMap Deutschland</a>',
    maxZoom: 19
  }).addTo(map);

  const styles = {
    "lighting-assets": {
      pointToLayer: (_feature, latlng) => L.circleMarker(latlng, {
        radius: 5, color: "#b97922", weight: 1.5, fillColor: "#edbd68", fillOpacity: 0.9
      })
    },
    "street-segments": {
      style: feature => ({
        color: feature.properties?.lit_value === "yes" || feature.properties?.lit_value === "automatic" ? "#327d65" : "#9a9b8c",
        weight: 4, opacity: 0.8, lineCap: "round"
      })
    },
    "avoidance-areas": {
      style: { color: "#b76057", weight: 2, fillColor: "#d77f73", fillOpacity: 0.22 }
    }
  };
  const layers = new Map();
  const status = document.getElementById("data-status");
  const apiPaths = {
    "lighting-assets": "/api/lighting-assets/",
    "street-segments": "/api/street-segments/",
    "avoidance-areas": "/api/avoidance-areas/"
  };

  function popup(feature, layer) {
    const props = feature.properties || {};
    const heading = props.name || props.source_id || props.asset_type || "Mapped feature";
    const detail = props.lit_value ? `Lighting tag: ${props.lit_value}` : props.highway ? `Path type: ${props.highway}` : props.category || props.asset_type || "Source record";
    const content = document.createElement("div");
    const title = document.createElement("p");
    title.className = "feature-title";
    title.textContent = heading;
    const meta = document.createElement("p");
    meta.className = "feature-meta";
    meta.textContent = detail;
    content.append(title, meta);
    layer.bindPopup(content);
  }

  async function loadLayer(name, path, options) {
    try {
      const response = await fetch(path, { headers: { Accept: "application/geo+json, application/json" } });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      const layer = L.geoJSON(data, { ...options, onEachFeature: popup });
      layers.set(name, layer);
      return data.features?.length || 0;
    } catch (error) {
      console.error(`Could not load ${name}:`, error);
      return null;
    }
  }

  Promise.all(Object.entries(apiPaths).map(([name, path]) => loadLayer(name, path, styles[name])))
    .then(counts => {
      document.querySelectorAll("[data-layer]").forEach(input => {
        input.addEventListener("change", () => {
          const layer = layers.get(input.dataset.layer);
          if (!layer) return;
          if (input.checked) layer.addTo(map);
          else map.removeLayer(layer);
        });
      });
      const loaded = counts.filter(count => count !== null).length;
      const total = counts.reduce((sum, count) => sum + (count || 0), 0);
      status.textContent = loaded === counts.length
        ? `${total} mapped features available across ${loaded} layers.`
        : `Some map data could not be loaded (${loaded} of ${counts.length} layers).`;
    });

  document.getElementById("recenter").addEventListener("click", () => map.setView(origin, 13));
  map.on("zoomend", () => { document.getElementById("zoom-label").textContent = `Zoom ${map.getZoom()}`; });
})();



