import { summarise, comparison, MANAGERS, managerText, shortlistRows } from "./metrics.js";
const $ = (id) => document.getElementById(id),
  fmt = (n) => Number(n).toLocaleString("en-AU");
const escape = (s) =>
  String(s).replace(
    /[&<>"']/g,
    (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c],
  );
const COLOURS = { state: "#c2510f", council: "#006da3", mixed: "#7157a6" },
  clusterColours = ["#7157a6", "#965320", "#276e48", "#a2395d", "#3466a3"];
try {
  const [data, boundary, clusters, roads] = await Promise.all(
    ["results.json", "boundary.geojson", "clusters.geojson", "roads.json"].map(async (file) => {
      const r = await fetch(`data/${file}`);
      if (!r.ok) throw Error(file);
      return r.json();
    }),
  );
  const params = new URLSearchParams(location.search);
  for (const [id, key] of [
    ["list", "list"],
    ["budget", "cells"],
  ]) {
    const v = params.get(key);
    if (v && [...$(id).options].some((o) => o.value === v)) $(id).value = v;
  }
  $("cluster").insertAdjacentHTML(
    "beforeend",
    data.clusters.clusters
      .map(
        (c) => `<option value="${c.cluster}">Cluster ${c.cluster} (${c.events} crashes)</option>`,
      )
      .join(""),
  );
  if (
    params.get("points") &&
    [...$("cluster").options].some((o) => o.value === params.get("points"))
  )
    $("cluster").value = params.get("points");

  const map = L.map("map", { scrollWheelZoom: false, zoomSnap: 0.25 });
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  }).addTo(map);
  const outline = L.geoJSON(boundary, {
    interactive: false,
    style: { color: "#4d6f7b", weight: 1.5, fill: false, dashArray: "4 3" },
  }).addTo(map);
  const fitCity = () => map.fitBounds(outline.getBounds(), { padding: [8, 8] });
  map.fitBounds(outline.getBounds());
  const cellLayer = L.layerGroup().addTo(map),
    pointLayer = L.layerGroup().addTo(map),
    canvas = L.canvas({ padding: 0.5 });
  const roadName = (id) => {
    const c = roads.cells[id];
    return c.roads.length ? c.roads.join(" & ") : "No road recorded";
  };
  let selected = null,
    polygons = {},
    fitted = false;

  function drawPoints() {
    pointLayer.clearLayers();
    const filter = $("cluster").value;
    if (filter === "off") return;
    for (const f of clusters.features) {
      const a = f.properties;
      if (filter !== "all" && String(a.cluster) !== filter) continue;
      const noise = a.cluster < 0,
        [lon, lat] = f.geometry.coordinates;
      L.circleMarker([lat, lon], {
        renderer: canvas,
        radius: noise ? 2.5 : 3.5,
        weight: 0.5,
        color: "#fff",
        fillColor: noise ? "#596368" : clusterColours[a.cluster % clusterColours.length],
        fillOpacity: 0.8,
      })
        .bindTooltip(
          `${noise ? "Unclustered" : "Cluster " + a.cluster}: ${a.year}, ${escape(a.suburb)}`,
        )
        .addTo(pointLayer);
    }
  }

  function areaDetail(pan) {
    const row = currentRows().find((r) => r.cell_id === selected),
      cell = roads.cells[selected],
      label = $("list").value === "all" ? "Serious crashes" : "Serious crashes on these roads";
    $("area").value = selected;
    $("area-detail").innerHTML =
      `<p class="context">Rank ${row.rank} • square ${escape(selected)}</p><h3>${escape(roadName(selected))}</h3><p class="suburbs">${escape(row.suburbs)}</p><dl><dt>${label}, 2021–2023</dt><dd>${row.train}</dd><dt>${label}, 2024</dt><dd>${row.holdout}</dd><dt>Road manager</dt><dd>${escape(managerText(cell))}</dd><dt>Area inside the city</dt><dd>${cell.clipped_area_km2.toFixed(2)} km²</dd></dl>${cell.state_road && cell.manager !== "council" ? `<p class="caption">State road: ${escape(cell.state_road)}.</p>` : ""}<p class="caption">Road names are the streets most often recorded for serious crashes in this square, 2021–2023.</p>`;
    for (const [id, p] of Object.entries(polygons))
      p.setStyle({
        weight: id === selected ? 3 : 1,
        color: id === selected ? "#10232b" : "#fff",
        fillOpacity: id === selected ? 0.75 : 0.5,
      });
    if (pan && polygons[selected])
      map.flyTo(polygons[selected].getBounds().getCenter(), Math.max(map.getZoom(), 14), {
        duration: 0.6,
      });
  }

  function currentRows() {
    return shortlistRows(data, roads, $("list").value, Number($("budget").value));
  }

  function showShortlist() {
    const k = Number($("budget").value),
      list = $("list").value,
      rows = currentRows();
    if (!rows.some((r) => r.cell_id === selected))
      selected =
        params.get("area") && rows.some((r) => r.cell_id === params.get("area"))
          ? params.get("area")
          : rows[0].cell_id;
    $("shortlist-note").textContent =
      list === "all"
        ? "Ranked on serious crashes in 2021–2023. Checked against 2024."
        : `Ranked on serious crashes on ${list === "council" ? "council" : "state-controlled"} roads in 2021–2023. Checked against 2024. Added after the original 2024 check.`;
    $("table-caption").textContent =
      list === "all"
        ? "Squares ranked on 2021–2023 serious crashes, with 2024 for comparison"
        : `Squares ranked on 2021–2023 serious crashes on ${list === "council" ? "council" : "state-controlled"} roads; counts include only those roads`;
    $("area").innerHTML = rows
      .map(
        (r) =>
          `<option value="${r.cell_id}">${r.rank}. ${escape(roadName(r.cell_id))} (${escape(r.suburbs)})</option>`,
      )
      .join("");
    cellLayer.clearLayers();
    polygons = {};
    for (const r of rows) {
      const cell = roads.cells[r.cell_id];
      polygons[r.cell_id] = L.polygon(
        cell.outline.map(([lon, lat]) => [lat, lon]),
        { color: "#fff", weight: 1, fillColor: COLOURS[cell.manager], fillOpacity: 0.5 },
      )
        .bindTooltip(`${r.rank}. ${escape(roadName(r.cell_id))}`)
        .on("click", () => {
          selected = r.cell_id;
          areaDetail(false);
        })
        .addTo(cellLayer);
    }
    $("shortlist-rows").innerHTML = rows
      .map(
        (r) =>
          `<tr><td>${r.rank}</td><td><button class="area-link" data-cell="${r.cell_id}">${escape(roadName(r.cell_id))}</button><small>${escape(r.suburbs)} • ${r.cell_id}</small></td><td>${escape(MANAGERS[roads.cells[r.cell_id].manager])}</td><td class="num">${r.train}</td><td class="num">${r.holdout}</td></tr>`,
      )
      .join("");
    if (list === "all") {
      const b = comparison(data.evaluation, k, "count"),
        c = roads.concentration.find((x) => x.k === k);
      $("capture-summary").innerHTML =
        `<strong>${b.numerator} / ${b.denominator}</strong><p>2024 serious crashes inside these ${k} squares (${b.capture_pct.toFixed(1)}%).</p><p class="caption">The ${k} squares cover ${c.area_share_pct.toFixed(2)}% of the city, so they hold about ${Math.round(c.times_city_average)} times their share of serious crashes. Spread evenly by area, they would hold about ${c.expected_if_spread_by_area.toFixed(1)}.</p>`;
    } else {
      const m = roads.by_manager.find((x) => x.manager === list),
        b = m.budgets.find((x) => x.k === k),
        name = list === "council" ? "council" : "state-controlled";
      $("capture-summary").innerHTML =
        `<strong>${b.captured_by_own_shortlist} / ${m.holdout_serious}</strong><p>2024 serious crashes on ${name} roads inside these ${k} squares (${((100 * b.captured_by_own_shortlist) / m.holdout_serious).toFixed(1)}%).</p><p class="caption">The original top ${k} caught ${b.captured_by_combined_shortlist} of them.</p>`;
    }
    drawPoints();
    areaDetail(false);
    if (!fitted) {
      map.fitBounds(
        cellLayer.getLayers().reduce((b, l) => b.extend(l.getBounds()), L.latLngBounds([])),
        { padding: [30, 30] },
      );
      fitted = true;
    }
  }

  function descriptive() {
    const year = $("year").value,
      severity = $("severity").value,
      t = summarise(data.monthly, year, severity);
    $("totals").innerHTML = [
      ["crashes", "Casualty crashes"],
      ["serious_crashes", "Serious crashes"],
      ["serious_casualties", "People killed or hospitalised"],
    ]
      .map(
        ([key, label]) =>
          `<div class="total"><strong>${fmt(t[key])}</strong><span>${label}</span></div>`,
      )
      .join("");
    const years = year === "All" ? [2020, 2021, 2022, 2023, 2024] : [Number(year)],
      annual = years.map((y) => ({ year: y, ...summarise(data.monthly, String(y), severity) })),
      max = Math.max(1, ...annual.map((r) => r.crashes));
    $("annual").innerHTML = annual
      .map(
        (r) =>
          `<div class="year-row"><span>${r.year}</span><div class="bar" style="width:${(100 * r.crashes) / max}%" aria-hidden="true"></div><strong>${fmt(r.crashes)}</strong></div>`,
      )
      .join("");
  }

  const conc = roads.concentration.find((x) => x.k === 20),
    count20 = comparison(data.evaluation, 20, "count"),
    density20 = comparison(data.evaluation, 20, "density"),
    mg = roads.managers;
  $("headline").textContent =
    `20 squares, ${conc.area_share_pct.toFixed(2)}% of the city, held ${count20.capture_pct.toFixed(1)}% of 2024's serious crashes.`;
  $("headline-detail").textContent =
    `That is about ${Math.round(conc.times_city_average)} times the city average. Clustering caught ${density20.numerator} of ${density20.denominator} against ${count20.numerator} for simple counts, so the simpler method stays. ${mg.shortlist_cells.state} of the 20 squares are mostly on state-controlled roads, mainly the Pacific Motorway.`;
  $("manager-stats").innerHTML = [
    [`${mg.shortlist_cells.state} of 20`, "top squares are mostly on state-controlled roads"],
    [
      `${Math.round(100 * mg.shortlist_training.state_share)}%`,
      "of their 2021–2023 serious crashes were on state-controlled roads",
    ],
    [
      `${Math.round(100 * mg.citywide_training.state_share)}%`,
      "is the citywide figure for the same years",
    ],
  ]
    .map(([v, l]) => `<div class="total"><strong>${v}</strong><span>${l}</span></div>`)
    .join("");
  $("manager-rows").innerHTML = roads.by_manager
    .map((m) => {
      const b = m.budgets.find((x) => x.k === 20);
      return `<tr><td>${m.manager === "council" ? "Council roads" : "State-controlled roads"}</td><td class="num">${m.holdout_serious}</td><td class="num">${b.captured_by_combined_shortlist}</td><td class="num">${b.captured_by_own_shortlist}</td></tr>`;
    })
    .join("");
  $("cluster-summary").textContent =
    `${clusters.features.length} serious crashes with coordinates in 2021–2023: ${data.clusters.clusters.length} clusters and ${data.clusters.noise_events} unclustered crashes. Clusters do not change the count shortlist.`;
  $("cluster-rows").innerHTML =
    data.clusters.clusters
      .map(
        (c) =>
          `<tr><td>${c.cluster}</td><td class="num">${c.events}</td><td class="num">${fmt(Math.round(c.bounding_box_diagonal_m))}</td></tr>`,
      )
      .join("") +
    `<tr><td>Unclustered (−1)</td><td class="num">${data.clusters.noise_events}</td><td class="num">Not applicable</td></tr>`;
  $("comparison").innerHTML = ["count", "density"]
    .map((method, i) => {
      const r = comparison(data.evaluation, 20, method);
      return `<div class="compare-item ${i ? "alt" : ""}"><h3>${i ? "DBSCAN clustering" : "Simple counts"}</h3><strong>${r.capture_pct.toFixed(2)}%</strong><p>${r.numerator} of ${r.denominator} serious crashes in 2024, top 20 squares</p><p class="caption">${r.validation_refit_overlap} of 20 squares were also in the previous fit's top 20</p></div>`;
    })
    .join("");
  $("quality").innerHTML = [
    `${fmt(data.quality.analysis_crashes)} casualty crashes in 2020–2024`,
    `${fmt(data.quality.grid_cells)} squares in the grid`,
    `${data.quality.missing_coordinates} crashes missing coordinates`,
    `${data.quality.serious_outside_current_boundary} serious crashes just outside the current boundary, kept in the totals`,
  ]
    .map((s) => `<li>${s}</li>`)
    .join("");
  $("uncertainty").textContent =
    `${(data.uncertainty.training_zero_fraction * 100).toFixed(1)}% of squares had no serious crashes in 2021–2023. A Gamma-Poisson model pools those empty squares with the roads, so its good overall interval coverage says little about any single site. It was not used for decisions.`;
  $("snapshot").textContent =
    `Data snapshot ${data.snapshot_id}, downloaded 5 October 2026. Main window 2020–2024.`;

  $("list").addEventListener("change", showShortlist);
  $("budget").addEventListener("change", showShortlist);
  $("cluster").addEventListener("change", drawPoints);
  $("area").addEventListener("change", () => {
    selected = $("area").value;
    areaDetail(true);
  });
  $("reset-view").addEventListener("click", fitCity);
  ["year", "severity"].forEach((id) => $(id).addEventListener("change", descriptive));
  document.addEventListener("click", (e) => {
    const target = e.target.closest("button[data-cell]");
    if (target) {
      selected = target.dataset.cell;
      areaDetail(true);
      $("map").scrollIntoView({ behavior: "smooth", block: "center" });
    }
  });
  $("status").textContent = "Data loaded • 2020–2024 • Queensland Government open data";
  showShortlist();
  descriptive();
} catch (error) {
  $("status").className = "error";
  $("status").textContent =
    "The data could not be loaded. Please refresh the page. If the problem continues, the source repository linked below has the same files.";
  console.error(error);
}
