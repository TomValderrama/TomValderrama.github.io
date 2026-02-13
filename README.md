# TomValderrama.github.io
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Evaluador AFP v3 - Comparador de Fondos de Pensiones Chile</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/recharts/2.7.3/Recharts.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:#0a0c10;color:#f3f4f6;font-family:'Outfit',sans-serif}
  ::-webkit-scrollbar{width:4px;height:4px}
  ::-webkit-scrollbar-track{background:#111318}
  ::-webkit-scrollbar-thumb{background:#23272f;border-radius:2px}
  input[type=number]::-webkit-inner-spin-button{opacity:1}
  .tab-btn{padding:6px 12px;border-radius:7px;border:1px solid #23272f;background:#111318;
    color:#6b7280;font-family:'DM Mono',monospace;font-size:11px;font-weight:500;cursor:pointer;transition:all .15s}
  .tab-btn.active{border-color:#3b82f6;background:rgba(59,130,246,0.08);color:#60a5fa}
  .tab-btn:hover:not(.active){border-color:#374151;color:#9ca3af}
</style>
</head>
<body>
<div id="root"></div>
<script>
"use strict";
var useState = React.useState, useMemo = React.useMemo, useCallback = React.useCallback, createElement = React.createElement;
var LineChart = Recharts.LineChart, Line = Recharts.Line, XAxis = Recharts.XAxis, YAxis = Recharts.YAxis,
    Tooltip = Recharts.Tooltip, ResponsiveContainer = Recharts.ResponsiveContainer, Legend = Recharts.Legend,
    ReferenceLine = Recharts.ReferenceLine, AreaChart = Recharts.AreaChart, Area = Recharts.Area;
var e = createElement;

var AFP_NAMES = ["Capital", "Cuprum", "Habitat", "Modelo", "Planvital", "ProVida", "Uno"];
var FONDOS = ["A", "B", "C", "D", "E"];
var FONDO_COLORS = { A: "#ef4444", B: "#f97316", C: "#c084fc", D: "#3b82f6", E: "#22c55e" };
var FONDO_RISK = { A: "Mas riesgoso", B: "Riesgoso", C: "Intermedio", D: "Conservador", E: "Mas conservador" };

var COMISIONES = {
  Capital: 1.44, Cuprum: 1.44, Habitat: 1.27, Modelo: 0.58,
  Planvital: 1.16, ProVida: 1.45, Uno: 0.49
};

var PROMEDIO_SP_CONFIRMADO = { A: 5.83, B: 5.13, C: 4.60, D: 3.93, E: 3.29 };

var INITIAL_HISTORICO = {
  2003: { A: 22.53, B: 14.15, C: 10.06, D: 8.27,  E: 3.45,  src: "UChile/SP" },
  2004: { A: 10.42, B: 8.13,  C: 7.05,  D: 6.28,  E: 4.89,  src: "UChile/SP" },
  2005: { A: 7.83,  B: 5.94,  C: 4.58,  D: 3.47,  E: 2.53,  src: "UChile/SP" },
  2006: { A: 18.84, B: 14.52, C: 10.75, D: 7.12,  E: 3.28,  src: "UChile/SP" },
  2007: { A: 13.81, B: 11.24, C: 8.36,  D: 5.48,  E: 2.15,  src: "UChile/SP" },
  2008: { A:-29.53, B:-22.49, C:-14.86, D:-7.98,  E:-0.93,  src: "UChile/SP" },
  2009: { A: 43.50, B: 33.36, C: 22.38, D: 12.80, E: 5.98,  src: "UChile/SP" },
  2010: { A: 10.38, B: 10.16, C: 7.93,  D: 5.67,  E: 4.23,  src: "UChile/SP" },
  2011: { A:-11.13, B:-7.18,  C:-3.08,  D: 1.12,  E: 5.72,  src: "UChile/SP" },
  2012: { A: 6.26,  B: 4.88,  C: 3.89,  D: 3.20,  E: 2.98,  src: "UChile/SP" },
  2013: { A: null,  B: null,  C: null,  D: null,  E: null,  src: "pendiente" },
  2014: { A: null,  B: null,  C: null,  D: null,  E: null,  src: "pendiente" },
  2015: { A: null,  B: null,  C: null,  D: null,  E: null,  src: "pendiente" },
  2016: { A: null,  B: null,  C: null,  D: null,  E: null,  src: "pendiente" },
  2017: { A: null,  B: null,  C: null,  D: null,  E: null,  src: "pendiente" },
  2018: { A: null,  B: null,  C: null,  D: null,  E: null,  src: "pendiente" },
  2019: { A: null,  B: null,  C: null,  D: null,  E: null,  src: "pendiente" },
  2020: { A: 1.74,  B: 3.38,  C: 4.32,  D: 4.12,  E: 4.47,  src: "SP 2020" },
  2021: { A: null,  B: null,  C: null,  D: null,  E: null,  src: "pendiente" },
  2022: { A:-20.81, B:-15.82, C:-9.21,  D: 0.63,  E: 7.83,  src: "SP 2022" },
  2023: { A: 7.18,  B: 6.06,  C: 3.04,  D:-0.04,  E:-1.31,  src: "SP 2023" },
  2024: { A: 9.10,  B: 7.44,  C: 3.35,  D: 0.10,  E: 0.31,  src: "SP 2024" },
  2025: { A: 14.89, B: 13.14, C: 12.18, D: 10.47, E: 8.06,  src: "SP 2025" },
};

function fmt(n) {
  if (n == null) return "-";
  if (Math.abs(n) >= 1e12) return "$" + (n / 1e12).toFixed(1) + "T";
  if (Math.abs(n) >= 1e9) return "$" + (n / 1e9).toFixed(1) + "B";
  if (Math.abs(n) >= 1e6) return "$" + (n / 1e6).toFixed(1) + "M";
  return "$" + Math.round(n).toLocaleString("es-CL");
}
function fmtFull(n) { return "$" + Math.round(n).toLocaleString("es-CL"); }

function simProyeccion(ahorro, sueldo, comPct, rentAnual, anios) {
  var r = [], s = ahorro;
  var cot = sueldo * 0.1, com = sueldo * (comPct / 100);
  var rm = Math.pow(1 + rentAnual / 100, 1 / 12) - 1;
  for (var y = 1; y <= anios; y++) {
    for (var m = 0; m < 12; m++) s = s * (1 + rm) + cot - com;
    r.push({ anio: y, saldo: s });
  }
  return r;
}

function simHistorico(ahorro, sueldo, comPct, datos, promSP) {
  var r = [], s = ahorro;
  var cot = sueldo * 0.1, com = sueldo * (comPct / 100);
  for (var i = 0; i < datos.length; i++) {
    var d = datos[i];
    var rentReal = d.rent != null ? d.rent : promSP;
    var rm = Math.pow(1 + rentReal / 100, 1 / 12) - 1;
    for (var m = 0; m < 12; m++) s = s * (1 + rm) + cot - com;
    r.push({ anio: d.anio, saldo: s, usedFallback: d.rent == null });
  }
  return r;
}

var medalC = ["#ffd700", "#c0c0c0", "#cd7f32"];

function RankRow(props) {
  var item = props.item, idx = props.idx, best = props.best;
  var medal = idx < 3;
  var barW = best > 0 ? Math.max(2, (item.saldo / best) * 100) : 0;
  return e("div", { style: {
    display: "grid", gridTemplateColumns: "28px 1fr 130px", alignItems: "center", gap: 8,
    padding: "7px 10px", background: medal ? medalC[idx] + "08" : "#111318",
    borderRadius: 8, border: medal ? "1px solid " + medalC[idx] + "33" : "1px solid #23272f",
    opacity: Math.max(0.45, 1 - idx * 0.03),
  }},
    e("span", { style: { fontFamily: "'DM Mono',monospace", fontSize: medal ? 15 : 11, fontWeight: 700,
      color: medal ? medalC[idx] : "#6b7280", textAlign: "center" }}, idx + 1),
    e("div", null,
      e("div", { style: { display: "flex", alignItems: "baseline", gap: 5, flexWrap: "wrap" }},
        e("span", { style: { fontFamily: "'DM Mono',monospace", fontSize: 12, fontWeight: 600,
          color: medal ? "#f3f4f6" : "#d1d5db" }}, item.afp),
        e("span", { style: { fontFamily: "'DM Mono',monospace", fontSize: 10, fontWeight: 700,
          color: FONDO_COLORS[item.fondo], background: FONDO_COLORS[item.fondo] + "15",
          padding: "1px 5px", borderRadius: 4 }}, "Fondo " + item.fondo),
        e("span", { style: { color: "#6b7280", fontSize: 9, fontFamily: "'DM Mono',monospace" }},
          "com " + item.com + "%" + (item.prom != null ? " | rent " + (item.prom > 0 ? "+" : "") + item.prom.toFixed(1) + "%" : ""))
      ),
      e("div", { style: { height: 2, background: "#1f2937", borderRadius: 2, marginTop: 3, overflow: "hidden" }},
        e("div", { style: { height: "100%", width: barW + "%", borderRadius: 2,
          background: medal ? medalC[idx] + "55" : "#3b82f644" }}))
    ),
    e("span", { style: { fontFamily: "'DM Mono',monospace", fontSize: 12, fontWeight: 700,
      color: medal ? "#f3f4f6" : "#d1d5db", textAlign: "right" }}, fmt(item.saldo))
  );
}

function AFPEvaluatorV3() {
  var _ahorro = useState(5000000), ahorro = _ahorro[0], setAhorro = _ahorro[1];
  var _sueldo = useState(1000000), sueldo = _sueldo[0], setSueldo = _sueldo[1];
  var _edad = useState(30), edad = _edad[0], setEdad = _edad[1];
  var _aniosProy = useState(30), aniosProy = _aniosProy[0], setAniosProy = _aniosProy[1];
  var _tab = useState("proyeccion"), tab = _tab[0], setTab = _tab[1];
  var _projYear = useState(5), projYear = _projYear[0], setProjYear = _projYear[1];
  var _cruzAfp = useState("Uno"), cruzAfp = _cruzAfp[0], setCruzAfp = _cruzAfp[1];
  var _cruzFondos = useState(["A", "D"]), cruzFondos = _cruzFondos[0], setCruzFondos = _cruzFondos[1];
  var _historico = useState(JSON.parse(JSON.stringify(INITIAL_HISTORICO))), historico = _historico[0], setHistorico = _historico[1];
  var _histStart = useState(2003), histStart = _histStart[0], setHistStart = _histStart[1];
  var _histEnd = useState(2025), histEnd = _histEnd[0], setHistEnd = _histEnd[1];
  var _editingHist = useState(false), editingHist = _editingHist[0], setEditingHist = _editingHist[1];

  var allYears = Object.keys(historico).map(Number).sort();
  var rangeYears = allYears.filter(function(y) { return y >= histStart && y <= histEnd; });

  var updateHistCell = useCallback(function(year, fondo, val) {
    setHistorico(function(prev) {
      var next = Object.assign({}, prev);
      next[year] = Object.assign({}, prev[year]);
      next[year][fondo] = val === "" ? null : Number(val);
      if (val !== "" && val !== null) next[year].src = "manual";
      return next;
    });
  }, []);

  var toggleCruzFondo = function(f) {
    setCruzFondos(function(prev) {
      return prev.includes(f)
        ? (prev.length > 1 ? prev.filter(function(x) { return x !== f; }) : prev)
        : prev.concat([f]);
    });
  };

  var datosReales = useMemo(function() {
    var total = 0, reales = 0;
    rangeYears.forEach(function(y) {
      FONDOS.forEach(function(f) {
        total++;
        if (historico[y] && historico[y][f] != null) reales++;
      });
    });
    return { total: total, reales: reales, pct: total > 0 ? Math.round(reales / total * 100) : 0 };
  }, [historico, rangeYears]);

  var projRankings = useMemo(function() {
    var porAnio = {};
    AFP_NAMES.forEach(function(afp) {
      FONDOS.forEach(function(fondo) {
        var sim = simProyeccion(ahorro, sueldo, COMISIONES[afp], PROMEDIO_SP_CONFIRMADO[fondo], aniosProy);
        sim.forEach(function(s) {
          if (!porAnio[s.anio]) porAnio[s.anio] = [];
          porAnio[s.anio].push({ afp: afp, fondo: fondo, com: COMISIONES[afp],
            prom: PROMEDIO_SP_CONFIRMADO[fondo], saldo: s.saldo });
        });
      });
    });
    Object.values(porAnio).forEach(function(arr) { arr.sort(function(a, b) { return b.saldo - a.saldo; }); });
    return porAnio;
  }, [ahorro, sueldo, aniosProy]);

  var acumRanking = useMemo(function() {
    var items = [];
    AFP_NAMES.forEach(function(afp) {
      FONDOS.forEach(function(fondo) {
        var datos = rangeYears.map(function(y) {
          return { anio: y, rent: historico[y] ? (historico[y][fondo] != null ? historico[y][fondo] : null) : null };
        });
        var sim = simHistorico(ahorro, sueldo, COMISIONES[afp], datos, PROMEDIO_SP_CONFIRMADO[fondo]);
        var last = sim[sim.length - 1];
        var usedFallbacks = sim.filter(function(s) { return s.usedFallback; }).length;
        items.push({ afp: afp, fondo: fondo, com: COMISIONES[afp], prom: PROMEDIO_SP_CONFIRMADO[fondo],
          saldo: last ? last.saldo : ahorro, fallbacks: usedFallbacks });
      });
    });
    items.sort(function(a, b) { return b.saldo - a.saldo; });
    return items;
  }, [ahorro, sueldo, historico, rangeYears]);

  var cruceData = useMemo(function() {
    var com = COMISIONES[cruzAfp];
    var data = [];
    var sims = {};
    cruzFondos.forEach(function(f) {
      sims[f] = simProyeccion(ahorro, sueldo, com, PROMEDIO_SP_CONFIRMADO[f], aniosProy);
    });
    for (var y = 0; y <= aniosProy; y++) {
      var pt = { anio: y };
      cruzFondos.forEach(function(f) { pt["Fondo " + f] = y === 0 ? ahorro : (sims[f][y - 1] ? sims[f][y - 1].saldo : 0); });
      data.push(pt);
    }
    var cruces = [];
    if (cruzFondos.length >= 2) {
      for (var i = 0; i < cruzFondos.length; i++) {
        for (var j = i + 1; j < cruzFondos.length; j++) {
          var f1 = cruzFondos[i], f2 = cruzFondos[j];
          for (var k = 1; k < data.length; k++) {
            var p1 = data[k-1]["Fondo " + f1], p2 = data[k-1]["Fondo " + f2];
            var c1 = data[k]["Fondo " + f1], c2 = data[k]["Fondo " + f2];
            if ((p1 <= p2 && c1 > c2) || (p1 >= p2 && c1 < c2)) {
              cruces.push({ anio: k, f1: f1, f2: f2, gana: c1 > c2 ? f1 : f2, diff: Math.abs(c1 - c2) });
            }
          }
        }
      }
    }
    return { data: data, cruces: cruces };
  }, [cruzAfp, cruzFondos, ahorro, sueldo, aniosProy]);

  var histChartData = useMemo(function() {
    return allYears.map(function(y) {
      var d = { anio: y };
      FONDOS.forEach(function(f) { d["Fondo " + f] = historico[y] ? historico[y][f] : null; });
      return d;
    }).filter(function(d) { return FONDOS.some(function(f) { return d["Fondo " + f] != null; }); });
  }, [historico, allYears]);

  var escenarios = useMemo(function() {
    var com = COMISIONES[cruzAfp];
    return cruzFondos.map(function(f) {
      var base = PROMEDIO_SP_CONFIRMADO[f];
      return {
        fondo: f,
        sc: [
          { name: "Pesimista", rent: base * 0.5 },
          { name: "Historico SP", rent: base },
          { name: "Optimista", rent: base * 1.5 },
        ].map(function(s) {
          var sim = simProyeccion(ahorro, sueldo, com, s.rent, aniosProy);
          return { name: s.name, rent: s.rent, final: sim[aniosProy - 1] ? sim[aniosProy - 1].saldo : 0 };
        }),
      };
    });
  }, [cruzAfp, cruzFondos, ahorro, sueldo, aniosProy]);

  var currentList = tab === "acumulado" ? acumRanking : (projRankings[projYear] || []);
  var best = currentList[0] ? currentList[0].saldo : 1;

  var tabsDef = [
    { id: "proyeccion", label: "Proyeccion" },
    { id: "cruce", label: "Cuando gana A?" },
    { id: "acumulado", label: "Acumulado" },
    { id: "datos", label: "Datos" },
  ];

  var P = { padding: 14, background: "#111318", borderRadius: 10, border: "1px solid #23272f", marginBottom: 14 };
  var L = { display: "block", fontSize: 10, fontWeight: 600, color: "#6b7280", marginBottom: 3,
    fontFamily: "'DM Mono',monospace", textTransform: "uppercase", letterSpacing: "0.4px" };
  var I = { width: "100%", background: "#0a0c10", border: "1px solid #23272f", color: "#f3f4f6",
    borderRadius: 7, padding: "7px 9px", fontSize: 13, fontFamily: "'DM Mono',monospace", fontWeight: 600, outline: "none" };
  var thS = { padding: "3px 4px", borderBottom: "1px solid #374151", textAlign: "left", color: "#9ca3af", fontWeight: 600, fontSize: 9 };
  var tdS = { padding: "2px 4px", borderBottom: "1px solid #1f2937", fontSize: 10 };

  function renderRankList(list, limit) {
    var shown = list.slice(0, limit);
    var rest = list.slice(limit);
    var items = shown.map(function(item, idx) {
      return e(RankRow, { key: item.afp + "-" + item.fondo, item: item, idx: idx, best: best });
    });
    var container = e("div", { style: { display: "flex", flexDirection: "column", gap: 3 }}, items);
    if (rest.length > 0) {
      var restItems = rest.map(function(item, idx) {
        return e(RankRow, { key: item.afp + "-" + item.fondo, item: item, idx: idx + limit, best: best });
      });
      return e("div", null, container,
        e("details", { style: { marginTop: 6 }},
          e("summary", { style: { color: "#60a5fa", cursor: "pointer", fontFamily: "'DM Mono',monospace", fontSize: 11, padding: 4 }},
            "Ver todo (" + list.length + ")"),
          e("div", { style: { display: "flex", flexDirection: "column", gap: 2, marginTop: 4 }}, restItems)
        )
      );
    }
    return container;
  }

  // ========== TAB: PROYECCION ==========
  function renderProyeccion() {
    return e("div", null,
      e("div", { style: P },
        e("div", { style: { display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 6 }},
          e("div", null,
            e("h2", { style: { fontFamily: "'DM Mono',monospace", fontSize: 15, fontWeight: 700, margin: 0 }},
              "Proyeccion anio " + projYear + " (" + (new Date().getFullYear() + projYear) + ")"),
            e("p", { style: { fontFamily: "'DM Mono',monospace", fontSize: 10, color: "#6b7280", margin: "2px 0 0" }},
              "Edad: " + (edad + projYear) + " | Basado en promedios confirmados SP")
          ),
          e("div", { style: { display: "flex", alignItems: "center", gap: 6 }},
            e("input", { type: "range", min: 1, max: aniosProy, value: projYear,
              onChange: function(ev) { setProjYear(Number(ev.target.value)); },
              style: { width: 140, accentColor: "#3b82f6" }}),
            e("span", { style: { fontFamily: "'DM Mono',monospace", fontSize: 16, fontWeight: 700, color: "#60a5fa", minWidth: 28 }},
              projYear)
          )
        )
      ),
      renderRankList(currentList, 15)
    );
  }

  // ========== TAB: CRUCE ==========
  function renderCruce() {
    return e("div", null,
      e("div", { style: P },
        e("div", { style: { display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap", marginBottom: 12 }},
          e("div", null,
            e("label", { style: L }, "AFP"),
            e("select", { value: cruzAfp, onChange: function(ev) { setCruzAfp(ev.target.value); },
              style: Object.assign({}, I, { width: "auto", padding: "6px 8px", fontSize: 12, cursor: "pointer" })},
              AFP_NAMES.map(function(a) { return e("option", { key: a, value: a }, a + " (" + COMISIONES[a] + "%)"); })
            )
          ),
          e("div", null,
            e("label", { style: L }, "Fondos a comparar"),
            e("div", { style: { display: "flex", gap: 3 }},
              FONDOS.map(function(f) {
                return e("button", { key: f, onClick: function() { toggleCruzFondo(f); }, style: {
                  padding: "4px 9px", borderRadius: 5, cursor: "pointer", fontFamily: "'DM Mono',monospace",
                  fontSize: 11, fontWeight: 600,
                  border: cruzFondos.includes(f) ? "2px solid " + FONDO_COLORS[f] : "1px solid #23272f",
                  background: cruzFondos.includes(f) ? FONDO_COLORS[f] + "18" : "#0a0c10",
                  color: cruzFondos.includes(f) ? FONDO_COLORS[f] : "#6b7280",
                }}, f);
              })
            )
          )
        ),
        e("div", { style: { width: "100%", height: 280 }},
          e(ResponsiveContainer, null,
            e(LineChart, { data: cruceData.data, margin: { top: 6, right: 12, bottom: 6, left: 6 }},
              e(XAxis, { dataKey: "anio", stroke: "#6b7280", fontSize: 9, fontFamily: "'DM Mono',monospace",
                tickFormatter: function(v) { return v + "a"; }}),
              e(YAxis, { stroke: "#6b7280", fontSize: 9, fontFamily: "'DM Mono',monospace",
                tickFormatter: function(v) { return fmt(v); }, width: 68 }),
              e(Tooltip, { contentStyle: { background: "#111318", border: "1px solid #23272f",
                borderRadius: 8, fontFamily: "'DM Mono',monospace", fontSize: 10 },
                formatter: function(v, n) { return [fmtFull(v), n]; },
                labelFormatter: function(v) { return "Anio " + v + " (edad " + (edad + v) + ")"; }}),
              e(Legend, { wrapperStyle: { fontFamily: "'DM Mono',monospace", fontSize: 10 }}),
              cruzFondos.map(function(f) {
                return e(Line, { key: f, type: "monotone", dataKey: "Fondo " + f,
                  stroke: FONDO_COLORS[f], strokeWidth: 2.5, dot: false });
              }),
              cruceData.cruces.map(function(c, i) {
                return e(ReferenceLine, { key: i, x: c.anio, stroke: "#fbbf24", strokeDasharray: "4 4", strokeWidth: 1.5 });
              })
            )
          )
        ),
        cruceData.cruces.length > 0 ?
          e("div", { style: { marginTop: 10, padding: 10, background: "#0a0c10", borderRadius: 7, border: "1px solid #fbbf2433" }},
            e("p", { style: { fontFamily: "'DM Mono',monospace", fontSize: 11, color: "#fbbf24", margin: "0 0 4px", fontWeight: 600 }},
              "Puntos de cruce:"),
            cruceData.cruces.map(function(c, i) {
              return e("p", { key: i, style: { fontFamily: "'DM Mono',monospace", fontSize: 10, color: "#f3f4f6", margin: "2px 0" }},
                "Anio " + c.anio + " (edad " + (edad + c.anio) + "): Fondo " + c.gana + " supera a Fondo " + (c.gana === c.f1 ? c.f2 : c.f1) + " por " + fmt(c.diff));
            })
          )
        : cruzFondos.length >= 2 ?
          e("div", { style: { marginTop: 10, padding: 10, background: "#0a0c10", borderRadius: 7, border: "1px solid #ef444433" }},
            e("p", { style: { fontFamily: "'DM Mono',monospace", fontSize: 11, color: "#ef4444", margin: 0 }},
              "Sin cruce en " + aniosProy + " anios. El fondo con mayor rentabilidad lidera desde el inicio.")
          )
        : null
      ),
      // Escenarios
      e("div", { style: P },
        e("h3", { style: { fontFamily: "'DM Mono',monospace", fontSize: 12, fontWeight: 700, margin: "0 0 8px" }},
          "Escenarios al anio " + aniosProy + " con " + cruzAfp),
        e("div", { style: { display: "grid", gridTemplateColumns: "repeat(" + Math.min(cruzFondos.length, 3) + ", 1fr)", gap: 8 }},
          escenarios.map(function(esc) {
            return e("div", { key: esc.fondo, style: { background: "#0a0c10", borderRadius: 7, padding: 10,
              border: "1px solid " + FONDO_COLORS[esc.fondo] + "22" }},
              e("div", { style: { display: "flex", alignItems: "center", gap: 5, marginBottom: 6 }},
                e("span", { style: { fontFamily: "'DM Mono',monospace", fontSize: 13, fontWeight: 700,
                  color: FONDO_COLORS[esc.fondo] }}, "Fondo " + esc.fondo),
                e("span", { style: { fontFamily: "'DM Mono',monospace", fontSize: 8, color: "#6b7280" }}, FONDO_RISK[esc.fondo])
              ),
              esc.sc.map(function(s) {
                return e("div", { key: s.name, style: { display: "flex", justifyContent: "space-between",
                  padding: "4px 0", borderBottom: "1px solid #1f2937" }},
                  e("span", { style: { fontFamily: "'DM Mono',monospace", fontSize: 10, color: "#6b7280" }},
                    s.name + " (" + s.rent.toFixed(1) + "%)"),
                  e("span", { style: { fontFamily: "'DM Mono',monospace", fontSize: 10, fontWeight: 600, color: "#f3f4f6" }},
                    fmt(s.final))
                );
              })
            );
          })
        )
      )
    );
  }

  // ========== TAB: ACUMULADO ==========
  function renderAcumulado() {
    return e("div", null,
      e("div", { style: P },
        e("h2", { style: { fontFamily: "'DM Mono',monospace", fontSize: 15, fontWeight: 700, margin: "0 0 3px" }},
          "Acumulado historico " + histStart + "-" + histEnd),
        e("p", { style: { fontFamily: "'DM Mono',monospace", fontSize: 10, color: "#6b7280", margin: "0 0 8px" }},
          "Simula haber estado en cada AFP+fondo durante el periodo.",
          datosReales.pct < 100 ? e("span", { style: { color: "#f97316" }},
            " Los anios sin datos usan el promedio SP como fallback (" + datosReales.reales + "/" + datosReales.total + " celdas con datos reales = " + datosReales.pct + "%).") : null
        ),
        e("div", { style: { display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }},
          e("div", null,
            e("label", { style: L }, "Desde"),
            e("select", { value: histStart, onChange: function(ev) { setHistStart(Number(ev.target.value)); },
              style: Object.assign({}, I, { width: 82, padding: "5px 6px", fontSize: 12 })},
              allYears.map(function(y) { return e("option", { key: y, value: y }, y); })
            )
          ),
          e("div", null,
            e("label", { style: L }, "Hasta"),
            e("select", { value: histEnd, onChange: function(ev) { setHistEnd(Number(ev.target.value)); },
              style: Object.assign({}, I, { width: 82, padding: "5px 6px", fontSize: 12 })},
              allYears.filter(function(y) { return y >= histStart; }).map(function(y) { return e("option", { key: y, value: y }, y); })
            )
          ),
          e("span", { style: { fontFamily: "'DM Mono',monospace", fontSize: 11, color: "#60a5fa", marginTop: 14 }},
            "= " + (histEnd - histStart + 1) + " anios")
        )
      ),
      renderRankList(acumRanking, 15)
    );
  }

  // ========== TAB: DATOS ==========
  function renderDatos() {
    return e("div", { style: P },
      e("div", { style: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10, flexWrap: "wrap", gap: 6 }},
        e("div", null,
          e("h2", { style: { fontFamily: "'DM Mono',monospace", fontSize: 15, fontWeight: 700, margin: 0 }},
            "Datos historicos anuales"),
          e("p", { style: { fontFamily: "'DM Mono',monospace", fontSize: 10, color: "#6b7280", margin: "2px 0 0" }},
            "Rentabilidad real anual promedio del sistema (%). null = sin dato, usa promedio SP.")
        ),
        e("button", { onClick: function() { setEditingHist(!editingHist); }, style: {
          padding: "5px 12px", borderRadius: 6, cursor: "pointer",
          fontFamily: "'DM Mono',monospace", fontSize: 11, fontWeight: 600,
          border: editingHist ? "1px solid #22c55e" : "1px solid #3b82f6",
          background: editingHist ? "#22c55e18" : "#3b82f618",
          color: editingHist ? "#22c55e" : "#60a5fa",
        }}, editingHist ? "Listo" : "Editar datos")
      ),
      histChartData.length > 0 ? e("div", { style: { width: "100%", height: 250, marginBottom: 12 }},
        e(ResponsiveContainer, null,
          e(AreaChart, { data: histChartData, margin: { top: 6, right: 12, bottom: 6, left: 6 }},
            e(XAxis, { dataKey: "anio", stroke: "#6b7280", fontSize: 9, fontFamily: "'DM Mono',monospace" }),
            e(YAxis, { stroke: "#6b7280", fontSize: 9, fontFamily: "'DM Mono',monospace",
              tickFormatter: function(v) { return v + "%"; }}),
            e(Tooltip, { contentStyle: { background: "#111318", border: "1px solid #23272f",
              borderRadius: 8, fontFamily: "'DM Mono',monospace", fontSize: 10 },
              formatter: function(v, n) { return [v != null ? v.toFixed(2) + "%" : "sin dato", n]; }}),
            e(Legend, { wrapperStyle: { fontFamily: "'DM Mono',monospace", fontSize: 10 }}),
            e(ReferenceLine, { y: 0, stroke: "#6b728055", strokeDasharray: "3 3" }),
            FONDOS.map(function(f) {
              return e(Area, { key: f, type: "monotone", dataKey: "Fondo " + f,
                stroke: FONDO_COLORS[f], fill: FONDO_COLORS[f] + "18",
                strokeWidth: 1.5, dot: false, connectNulls: false });
            })
          )
        )
      ) : null,
      // Tabla
      e("div", { style: { overflowX: "auto" }},
        e("table", { style: { borderCollapse: "collapse", width: "100%", fontSize: 10, fontFamily: "'DM Mono',monospace" }},
          e("thead", null,
            e("tr", null,
              e("th", { style: thS }, "Anio"),
              FONDOS.map(function(f) { return e("th", { key: f, style: Object.assign({}, thS, { color: FONDO_COLORS[f] }) }, "F." + f); }),
              e("th", { style: thS }, "Fuente")
            )
          ),
          e("tbody", null,
            allYears.map(function(y) {
              var row = historico[y];
              return e("tr", { key: y, style: { background: row && row.src === "pendiente" ? "#f9731605" : "transparent" }},
                e("td", { style: tdS }, y),
                FONDOS.map(function(f) {
                  var v = row ? row[f] : null;
                  return e("td", { key: f, style: tdS },
                    editingHist ?
                      e("input", { type: "number", step: "0.01", value: v != null ? v : "",
                        placeholder: "null",
                        onChange: function(ev) { updateHistCell(y, f, ev.target.value); },
                        style: { width: 62, background: "#0a0c10", border: "1px solid #23272f",
                          color: "#f3f4f6", borderRadius: 4, padding: "2px 4px", fontSize: 10,
                          fontFamily: "'DM Mono',monospace", outline: "none" }})
                    :
                      e("span", { style: { color: v == null ? "#374151" : v >= 0 ? "#22c55e" : "#ef4444" }},
                        v != null ? (v > 0 ? "+" : "") + v.toFixed(1) + "%" : "null")
                  );
                }),
                e("td", { style: Object.assign({}, tdS, { fontSize: 8,
                  color: row && row.src === "pendiente" ? "#f97316" :
                         row && row.src === "manual" ? "#a78bfa" : "#4b5563" })},
                  row ? row.src : "")
              );
            })
          )
        )
      ),
      e("div", { style: { marginTop: 10, padding: 10, background: "#0a0c10", borderRadius: 7, border: "1px solid #3b82f622" }},
        e("p", { style: { fontFamily: "'DM Mono',monospace", fontSize: 10, color: "#60a5fa", margin: "0 0 4px", fontWeight: 600 }},
          "Como obtener los datos faltantes:"),
        e("ol", { style: { fontFamily: "'DM Mono',monospace", fontSize: 10, color: "#9ca3af", margin: 0,
          paddingLeft: 16, lineHeight: 1.8 }},
          e("li", null, "Ir a spensiones.cl > Informes > Fondos de Pensiones > Rentabilidad Mensual"),
          e("li", null, "Abrir el informe de diciembre de cada anio"),
          e("li", null, 'Buscar la tabla "Rentabilidad Real de los Fondos de Pensiones" (12 meses)'),
          e("li", null, 'Tomar la fila "Promedio del Sistema" para cada fondo'),
          e("li", null, 'Click "Editar datos" arriba e ingresar los valores')
        )
      )
    );
  }

  // ========== MAIN RENDER ==========
  return e("div", { style: { minHeight: "100vh", background: "#0a0c10", color: "#f3f4f6",
    fontFamily: "'Outfit',sans-serif", padding: "16px 12px" }},
    e("div", { style: { maxWidth: 920, margin: "0 auto" }},
      // Header
      e("div", { style: { marginBottom: 20 }},
        e("h1", { style: { fontSize: 22, fontWeight: 700, color: "#60a5fa", margin: 0,
          fontFamily: "'DM Mono',monospace" }}, "Evaluador AFP v3"),
        e("p", { style: { color: "#6b7280", fontSize: 11, marginTop: 3, fontFamily: "'DM Mono',monospace" }},
          "Promedios confirmados por SP (sept 2002 - ene 2026) + datos anuales editables")
      ),
      // Inputs
      e("div", { style: Object.assign({}, P, { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(145px, 1fr))", gap: 10 })},
        e("div", null, e("label", { style: L }, "Ahorro actual ($)"),
          e("input", { type: "number", value: ahorro, onChange: function(ev) { setAhorro(Number(ev.target.value)); }, style: I })),
        e("div", null, e("label", { style: L }, "Sueldo imponible ($)"),
          e("input", { type: "number", value: sueldo, onChange: function(ev) { setSueldo(Number(ev.target.value)); }, style: I })),
        e("div", null, e("label", { style: L }, "Edad actual"),
          e("input", { type: "number", value: edad, onChange: function(ev) { setEdad(Number(ev.target.value)); }, style: I })),
        e("div", null, e("label", { style: L }, "Proyectar (anios)"),
          e("input", { type: "number", value: aniosProy, min: 1, max: 40,
            onChange: function(ev) { setAniosProy(Number(ev.target.value)); }, style: I }))
      ),
      // Promedios confirmados
      e("div", { style: Object.assign({}, P, { background: "#0f1115", border: "1px solid #22c55e22" })},
        e("p", { style: { fontFamily: "'DM Mono',monospace", fontSize: 10, color: "#22c55e", margin: "0 0 6px",
          textTransform: "uppercase", fontWeight: 600, letterSpacing: "0.5px" }},
          "Rentabilidad real promedio anual CONFIRMADA por SP (sept 2002 - ene 2026)"),
        e("div", { style: { display: "flex", gap: 14, flexWrap: "wrap" }},
          FONDOS.map(function(f) {
            return e("span", { key: f, style: { fontFamily: "'DM Mono',monospace", fontSize: 13 }},
              e("span", { style: { color: FONDO_COLORS[f], fontWeight: 700 }}, "Fondo " + f + ": "),
              e("span", { style: { color: "#22c55e" }}, "+" + PROMEDIO_SP_CONFIRMADO[f].toFixed(2) + "%")
            );
          })
        )
      ),
      // Tabs
      e("div", { style: { display: "flex", gap: 3, marginBottom: 12, flexWrap: "wrap" }},
        tabsDef.map(function(t) {
          return e("button", { key: t.id, onClick: function() { setTab(t.id); },
            className: "tab-btn" + (tab === t.id ? " active" : "") }, t.label);
        })
      ),
      // Tab content
      tab === "proyeccion" ? renderProyeccion() : null,
      tab === "cruce" ? renderCruce() : null,
      tab === "acumulado" ? renderAcumulado() : null,
      tab === "datos" ? renderDatos() : null,
      // Footer
      e("div", { style: Object.assign({}, P, { marginTop: 14, border: "1px solid #c084fc22" })},
        e("h3", { style: { fontFamily: "'DM Mono',monospace", fontSize: 11, fontWeight: 700, color: "#c084fc", margin: "0 0 5px" }},
          "Metodologia"),
        e("div", { style: { fontFamily: "'DM Mono',monospace", fontSize: 10, color: "#9ca3af", lineHeight: 1.7 }},
          e("p", { style: { margin: "0 0 5px" }},
            e("strong", { style: { color: "#f3f4f6" }}, "Proyecciones"), " usan los promedios reales confirmados por la SP (Fondo A: " + PROMEDIO_SP_CONFIRMADO.A + "%, ..., E: " + PROMEDIO_SP_CONFIRMADO.E + "%), identicos para todas las AFPs. Lo que diferencia una AFP de otra es unicamente la comision."),
          e("p", { style: { margin: "0 0 5px" }},
            e("strong", { style: { color: "#f3f4f6" }}, "Acumulado historico"), " usa datos anuales reales donde los hay, y el promedio SP como fallback donde faltan. El % de datos reales se muestra en pantalla."),
          e("p", { style: { margin: 0 }},
            "Con los promedios confirmados, el Fondo A (" + PROMEDIO_SP_CONFIRMADO.A + "%) tiene ~1.9pp mas que el D (" + PROMEDIO_SP_CONFIRMADO.D + "%). Esa diferencia compuesta a 30 anios es enorme. Pero el A tuvo anios de -29% (2008) y el D nunca bajo de -8%. La comision es la unica variable que controlas con certeza.")
        )
      )
    )
  );
}

ReactDOM.render(e(AFPEvaluatorV3), document.getElementById("root"));
</script>
</body>
</html>
