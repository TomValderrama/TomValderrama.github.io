# TomValderrama.github.io
import { useState, useMemo, useCallback } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, ReferenceLine, AreaChart, Area } from "recharts";

// ============================================================
// DATOS CONFIRMADOS
// ============================================================

const AFP_NAMES = ["Capital", "Cuprum", "Habitat", "Modelo", "Planvital", "ProVida", "Uno"];
const FONDOS = ["A", "B", "C", "D", "E"];
const FONDO_COLORS = { A: "#ef4444", B: "#f97316", C: "#c084fc", D: "#3b82f6", E: "#22c55e" };
const FONDO_RISK = { A: "Mas riesgoso", B: "Riesgoso", C: "Intermedio", D: "Conservador", E: "Mas conservador" };

// Comisiones vigentes feb 2026 (fuente: uno.cl, spensiones.cl)
const COMISIONES = {
  Capital: 1.44, Cuprum: 1.44, Habitat: 1.27, Modelo: 0.58,
  Planvital: 1.16, ProVida: 1.45, Uno: 0.49
};

// Rentabilidad real promedio anual CONFIRMADA por Habitat/SP
// Periodo: septiembre 2002 - enero 2026
// Fuente: afphabitat.cl/mejor-rentabilidad (cita SP directamente)
const PROMEDIO_SP_CONFIRMADO = {
  A: 5.83, B: 5.13, C: 4.60, D: 3.93, E: 3.29
};

// Datos anuales por tipo de fondo (promedio del sistema)
// Fuentes indicadas por fila. "SP" = confirmado en informe oficial.
// "UChile" = tesis U. de Chile con datos SP (periodo sept-sept, aprox a ene-dic).
// Donde no hay dato confirmado, se deja null y se usa el promedio SP para proyecciones.
//
// INSTRUCCIONES: Actualiza los null con datos reales de spensiones.cl
// Cada informe mensual de diciembre tiene la tabla anual completa.

const INITIAL_HISTORICO = {
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

// ============================================================
// UTILIDADES
// ============================================================

function fmt(n) {
  if (n == null) return "-";
  if (Math.abs(n) >= 1e12) return "$" + (n / 1e12).toFixed(1) + "T";
  if (Math.abs(n) >= 1e9) return "$" + (n / 1e9).toFixed(1) + "B";
  if (Math.abs(n) >= 1e6) return "$" + (n / 1e6).toFixed(1) + "M";
  return "$" + Math.round(n).toLocaleString("es-CL");
}
function fmtFull(n) { return "$" + Math.round(n).toLocaleString("es-CL"); }

function simProyeccion(ahorro, sueldo, comPct, rentAnual, anios) {
  const r = [];
  let s = ahorro;
  const cot = sueldo * 0.1;
  const com = sueldo * (comPct / 100);
  const rm = Math.pow(1 + rentAnual / 100, 1 / 12) - 1;
  for (let y = 1; y <= anios; y++) {
    for (let m = 0; m < 12; m++) s = s * (1 + rm) + cot - com;
    r.push({ anio: y, saldo: s });
  }
  return r;
}

function simHistorico(ahorro, sueldo, comPct, datos, promSP) {
  const r = [];
  let s = ahorro;
  const cot = sueldo * 0.1;
  const com = sueldo * (comPct / 100);
  for (const { anio, rent } of datos) {
    const rentReal = rent != null ? rent : promSP;
    const rm = Math.pow(1 + rentReal / 100, 1 / 12) - 1;
    for (let m = 0; m < 12; m++) s = s * (1 + rm) + cot - com;
    r.push({ anio, saldo: s, usedFallback: rent == null });
  }
  return r;
}

// ============================================================
// COMPONENTES
// ============================================================

const medalC = ["#ffd700", "#c0c0c0", "#cd7f32"];

function RankRow({ item, idx, best }) {
  const medal = idx < 3;
  const barW = best > 0 ? Math.max(2, (item.saldo / best) * 100) : 0;
  return (
    <div style={{
      display: "grid", gridTemplateColumns: "28px 1fr 130px", alignItems: "center", gap: 8,
      padding: "7px 10px", background: medal ? `${medalC[idx]}08` : "#111318",
      borderRadius: 8, border: medal ? `1px solid ${medalC[idx]}33` : "1px solid #23272f",
      opacity: Math.max(0.45, 1 - idx * 0.03),
    }}>
      <span style={{ fontFamily: "'DM Mono',monospace", fontSize: medal ? 15 : 11, fontWeight: 700,
        color: medal ? medalC[idx] : "#6b7280", textAlign: "center" }}>{idx + 1}</span>
      <div>
        <div style={{ display: "flex", alignItems: "baseline", gap: 5, flexWrap: "wrap" }}>
          <span style={{ fontFamily: "'DM Mono',monospace", fontSize: 12, fontWeight: 600,
            color: medal ? "#f3f4f6" : "#d1d5db" }}>{item.afp}</span>
          <span style={{ fontFamily: "'DM Mono',monospace", fontSize: 10, fontWeight: 700,
            color: FONDO_COLORS[item.fondo], background: FONDO_COLORS[item.fondo] + "15",
            padding: "1px 5px", borderRadius: 4 }}>Fondo {item.fondo}</span>
          <span style={{ color: "#6b7280", fontSize: 9, fontFamily: "'DM Mono',monospace" }}>
            com {item.com}%{item.prom != null && ` | rent ${item.prom > 0 ? "+" : ""}${item.prom.toFixed(1)}%`}
          </span>
        </div>
        <div style={{ height: 2, background: "#1f2937", borderRadius: 2, marginTop: 3, overflow: "hidden" }}>
          <div style={{ height: "100%", width: `${barW}%`, borderRadius: 2,
            background: medal ? medalC[idx] + "55" : "#3b82f644" }} />
        </div>
      </div>
      <span style={{ fontFamily: "'DM Mono',monospace", fontSize: 12, fontWeight: 700,
        color: medal ? "#f3f4f6" : "#d1d5db", textAlign: "right" }}>{fmt(item.saldo)}</span>
    </div>
  );
}

// ============================================================
// APP PRINCIPAL
// ============================================================

export default function AFPEvaluatorV3() {
  const [ahorro, setAhorro] = useState(5000000);
  const [sueldo, setSueldo] = useState(1000000);
  const [edad, setEdad] = useState(30);
  const [aniosProy, setAniosProy] = useState(30);
  const [tab, setTab] = useState("proyeccion");
  const [projYear, setProjYear] = useState(5);

  // Crossover state
  const [cruzAfp, setCruzAfp] = useState("Uno");
  const [cruzFondos, setCruzFondos] = useState(["A", "D"]);

  // Historico editable
  const [historico, setHistorico] = useState(JSON.parse(JSON.stringify(INITIAL_HISTORICO)));
  const [histStart, setHistStart] = useState(2003);
  const [histEnd, setHistEnd] = useState(2024);
  const [editingHist, setEditingHist] = useState(false);

  const allYears = Object.keys(historico).map(Number).sort();
  const rangeYears = allYears.filter(y => y >= histStart && y <= histEnd);

  const updateHistCell = useCallback((year, fondo, val) => {
    setHistorico(prev => {
      const next = { ...prev, [year]: { ...prev[year], [fondo]: val === "" ? null : Number(val) } };
      if (val !== "" && val !== null) next[year].src = "manual";
      return next;
    });
  }, []);

  const toggleCruzFondo = (f) => {
    setCruzFondos(prev => prev.includes(f)
      ? (prev.length > 1 ? prev.filter(x => x !== f) : prev)
      : [...prev, f]);
  };

  // Conteo de datos reales en rango
  const datosReales = useMemo(() => {
    let total = 0, reales = 0;
    rangeYears.forEach(y => {
      FONDOS.forEach(f => {
        total++;
        if (historico[y]?.[f] != null) reales++;
      });
    });
    return { total, reales, pct: total > 0 ? Math.round(reales / total * 100) : 0 };
  }, [historico, rangeYears]);

  // ========== PROYECCION RANKING ==========
  const projRankings = useMemo(() => {
    const porAnio = {};
    AFP_NAMES.forEach(afp => {
      FONDOS.forEach(fondo => {
        const sim = simProyeccion(ahorro, sueldo, COMISIONES[afp], PROMEDIO_SP_CONFIRMADO[fondo], aniosProy);
        sim.forEach(s => {
          if (!porAnio[s.anio]) porAnio[s.anio] = [];
          porAnio[s.anio].push({
            afp, fondo, com: COMISIONES[afp],
            prom: PROMEDIO_SP_CONFIRMADO[fondo], saldo: s.saldo
          });
        });
      });
    });
    Object.values(porAnio).forEach(arr => arr.sort((a, b) => b.saldo - a.saldo));
    return porAnio;
  }, [ahorro, sueldo, aniosProy]);

  // ========== ACUMULADO HISTORICO RANKING ==========
  const acumRanking = useMemo(() => {
    const items = [];
    AFP_NAMES.forEach(afp => {
      FONDOS.forEach(fondo => {
        const datos = rangeYears.map(y => ({
          anio: y, rent: historico[y]?.[fondo] ?? null
        }));
        const sim = simHistorico(ahorro, sueldo, COMISIONES[afp], datos, PROMEDIO_SP_CONFIRMADO[fondo]);
        const last = sim[sim.length - 1];
        const usedFallbacks = sim.filter(s => s.usedFallback).length;
        items.push({
          afp, fondo, com: COMISIONES[afp],
          prom: PROMEDIO_SP_CONFIRMADO[fondo],
          saldo: last?.saldo || ahorro,
          fallbacks: usedFallbacks,
        });
      });
    });
    items.sort((a, b) => b.saldo - a.saldo);
    return items;
  }, [ahorro, sueldo, historico, rangeYears]);

  // ========== CROSSOVER DATA ==========
  const cruceData = useMemo(() => {
    const com = COMISIONES[cruzAfp];
    const data = [];
    const sims = {};
    cruzFondos.forEach(f => {
      sims[f] = simProyeccion(ahorro, sueldo, com, PROMEDIO_SP_CONFIRMADO[f], aniosProy);
    });
    for (let y = 0; y <= aniosProy; y++) {
      const pt = { anio: y };
      cruzFondos.forEach(f => { pt[`Fondo ${f}`] = y === 0 ? ahorro : sims[f][y - 1]?.saldo || 0; });
      data.push(pt);
    }
    const cruces = [];
    if (cruzFondos.length >= 2) {
      for (let i = 0; i < cruzFondos.length; i++) {
        for (let j = i + 1; j < cruzFondos.length; j++) {
          const f1 = cruzFondos[i], f2 = cruzFondos[j];
          for (let k = 1; k < data.length; k++) {
            const p1 = data[k-1][`Fondo ${f1}`], p2 = data[k-1][`Fondo ${f2}`];
            const c1 = data[k][`Fondo ${f1}`], c2 = data[k][`Fondo ${f2}`];
            if ((p1 <= p2 && c1 > c2) || (p1 >= p2 && c1 < c2)) {
              cruces.push({ anio: k, f1, f2, gana: c1 > c2 ? f1 : f2, diff: Math.abs(c1 - c2) });
            }
          }
        }
      }
    }
    return { data, cruces };
  }, [cruzAfp, cruzFondos, ahorro, sueldo, aniosProy]);

  // ========== HISTORICO CHART DATA ==========
  const histChartData = useMemo(() => {
    return allYears.map(y => {
      const d = { anio: y };
      FONDOS.forEach(f => { d[`Fondo ${f}`] = historico[y]?.[f] ?? null; });
      return d;
    }).filter(d => FONDOS.some(f => d[`Fondo ${f}`] != null));
  }, [historico, allYears]);

  // ========== ESCENARIOS ==========
  const escenarios = useMemo(() => {
    const com = COMISIONES[cruzAfp];
    return cruzFondos.map(f => {
      const base = PROMEDIO_SP_CONFIRMADO[f];
      return {
        fondo: f,
        sc: [
          { name: "Pesimista", rent: base * 0.5 },
          { name: "Historico SP", rent: base },
          { name: "Optimista", rent: base * 1.5 },
        ].map(s => ({
          ...s,
          final: simProyeccion(ahorro, sueldo, com, s.rent, aniosProy)[aniosProy - 1]?.saldo || 0,
        })),
      };
    });
  }, [cruzAfp, cruzFondos, ahorro, sueldo, aniosProy]);

  const currentList = tab === "acumulado" ? acumRanking : (projRankings[projYear] || []);
  const best = currentList[0]?.saldo || 1;

  const tabs = [
    { id: "proyeccion", label: "Proyeccion" },
    { id: "cruce", label: "Cuando gana A?" },
    { id: "acumulado", label: "Acumulado" },
    { id: "datos", label: "Datos" },
    { id: "compartir", label: "Compartir" },
  ];

  const P = { padding: 14, background: "#111318", borderRadius: 10, border: "1px solid #23272f", marginBottom: 14 };
  const L = { display: "block", fontSize: 10, fontWeight: 600, color: "#6b7280", marginBottom: 3,
    fontFamily: "'DM Mono',monospace", textTransform: "uppercase", letterSpacing: "0.4px" };
  const I = { width: "100%", background: "#0a0c10", border: "1px solid #23272f", color: "#f3f4f6",
    borderRadius: 7, padding: "7px 9px", fontSize: 13, fontFamily: "'DM Mono',monospace", fontWeight: 600, outline: "none" };

  return (
    <div style={{ minHeight: "100vh", background: "#0a0c10", color: "#f3f4f6",
      fontFamily: "'Outfit',sans-serif", padding: "16px 12px" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Outfit:wght@400;500;600;700&display=swap');
        *{box-sizing:border-box} ::-webkit-scrollbar{width:4px;height:4px}
        ::-webkit-scrollbar-track{background:#111318} ::-webkit-scrollbar-thumb{background:#23272f;border-radius:2px}
        input[type=number]::-webkit-inner-spin-button{opacity:1}
        .tab-btn{padding:6px 12px;border-radius:7px;border:1px solid #23272f;background:#111318;
          color:#6b7280;font-family:'DM Mono',monospace;font-size:11px;font-weight:500;cursor:pointer;transition:all .15s}
        .tab-btn.active{border-color:#3b82f6;background:#3b82f615;color:#60a5fa}
        .tab-btn:hover:not(.active){border-color:#374151;color:#9ca3af}
      `}</style>

      <div style={{ maxWidth: 920, margin: "0 auto" }}>
        {/* HEADER */}
        <div style={{ marginBottom: 20 }}>
          <h1 style={{ fontSize: 22, fontWeight: 700, color: "#60a5fa", margin: 0,
            fontFamily: "'DM Mono',monospace" }}>Evaluador AFP v3</h1>
          <p style={{ color: "#6b7280", fontSize: 11, marginTop: 3, fontFamily: "'DM Mono',monospace" }}>
            Promedios confirmados por SP (sept 2002 - ene 2026) + datos anuales editables
          </p>
        </div>

        {/* INPUTS */}
        <div style={{ ...P, display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(145px, 1fr))", gap: 10 }}>
          <div><label style={L}>Ahorro actual ($)</label>
            <input type="number" value={ahorro} onChange={e => setAhorro(Number(e.target.value))} style={I} /></div>
          <div><label style={L}>Sueldo imponible ($)</label>
            <input type="number" value={sueldo} onChange={e => setSueldo(Number(e.target.value))} style={I} /></div>
          <div><label style={L}>Edad actual</label>
            <input type="number" value={edad} onChange={e => setEdad(Number(e.target.value))} style={I} /></div>
          <div><label style={L}>Proyectar (anios)</label>
            <input type="number" value={aniosProy} min={1} max={40}
              onChange={e => setAniosProy(Number(e.target.value))} style={I} /></div>
        </div>

        {/* PROMEDIOS CONFIRMADOS */}
        <div style={{ ...P, background: "#0f1115", border: "1px solid #22c55e22" }}>
          <p style={{ fontFamily: "'DM Mono',monospace", fontSize: 10, color: "#22c55e", margin: "0 0 6px",
            textTransform: "uppercase", fontWeight: 600, letterSpacing: "0.5px" }}>
            Rentabilidad real promedio anual CONFIRMADA por SP (sept 2002 - ene 2026)</p>
          <div style={{ display: "flex", gap: 14, flexWrap: "wrap" }}>
            {FONDOS.map(f => (
              <span key={f} style={{ fontFamily: "'DM Mono',monospace", fontSize: 13 }}>
                <span style={{ color: FONDO_COLORS[f], fontWeight: 700 }}>Fondo {f}: </span>
                <span style={{ color: "#22c55e" }}>+{PROMEDIO_SP_CONFIRMADO[f].toFixed(2)}%</span>
              </span>
            ))}
          </div>
        </div>

        {/* TABS */}
        <div style={{ display: "flex", gap: 3, marginBottom: 12, flexWrap: "wrap" }}>
          {tabs.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)}
              className={`tab-btn ${tab === t.id ? "active" : ""}`}>{t.label}</button>
          ))}
        </div>

        {/* ==================== PROYECCION ==================== */}
        {tab === "proyeccion" && (<>
          <div style={P}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 6 }}>
              <div>
                <h2 style={{ fontFamily: "'DM Mono',monospace", fontSize: 15, fontWeight: 700, margin: 0 }}>
                  Proyeccion anio {projYear} ({new Date().getFullYear() + projYear})</h2>
                <p style={{ fontFamily: "'DM Mono',monospace", fontSize: 10, color: "#6b7280", margin: "2px 0 0" }}>
                  Edad: {edad + projYear} | Basado en promedios confirmados SP</p>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <input type="range" min={1} max={aniosProy} value={projYear}
                  onChange={e => setProjYear(Number(e.target.value))}
                  style={{ width: 140, accentColor: "#3b82f6" }} />
                <span style={{ fontFamily: "'DM Mono',monospace", fontSize: 16, fontWeight: 700, color: "#60a5fa", minWidth: 28 }}>
                  {projYear}</span>
              </div>
            </div>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
            {currentList.slice(0, 15).map((item, idx) => (
              <RankRow key={`${item.afp}-${item.fondo}`} item={item} idx={idx} best={best} />
            ))}
          </div>
          {currentList.length > 15 && (
            <details style={{ marginTop: 6 }}>
              <summary style={{ color: "#60a5fa", cursor: "pointer", fontFamily: "'DM Mono',monospace", fontSize: 11, padding: 4 }}>
                Ver todo ({currentList.length})</summary>
              <div style={{ display: "flex", flexDirection: "column", gap: 2, marginTop: 4 }}>
                {currentList.slice(15).map((item, idx) => (
                  <RankRow key={`${item.afp}-${item.fondo}`} item={item} idx={idx + 15} best={best} />
                ))}
              </div>
            </details>
          )}
        </>)}

        {/* ==================== CROSSOVER ==================== */}
        {tab === "cruce" && (<>
          <div style={P}>
            <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap", marginBottom: 12 }}>
              <div>
                <label style={L}>AFP</label>
                <select value={cruzAfp} onChange={e => setCruzAfp(e.target.value)}
                  style={{ ...I, width: "auto", padding: "6px 8px", fontSize: 12, cursor: "pointer" }}>
                  {AFP_NAMES.map(a => <option key={a} value={a}>{a} ({COMISIONES[a]}%)</option>)}
                </select>
              </div>
              <div>
                <label style={L}>Fondos a comparar</label>
                <div style={{ display: "flex", gap: 3 }}>
                  {FONDOS.map(f => (
                    <button key={f} onClick={() => toggleCruzFondo(f)} style={{
                      padding: "4px 9px", borderRadius: 5, cursor: "pointer", fontFamily: "'DM Mono',monospace",
                      fontSize: 11, fontWeight: 600,
                      border: cruzFondos.includes(f) ? `2px solid ${FONDO_COLORS[f]}` : "1px solid #23272f",
                      background: cruzFondos.includes(f) ? FONDO_COLORS[f] + "18" : "#0a0c10",
                      color: cruzFondos.includes(f) ? FONDO_COLORS[f] : "#6b7280",
                    }}>{f}</button>
                  ))}
                </div>
              </div>
            </div>

            <div style={{ width: "100%", height: 280 }}>
              <ResponsiveContainer>
                <LineChart data={cruceData.data} margin={{ top: 6, right: 12, bottom: 6, left: 6 }}>
                  <XAxis dataKey="anio" stroke="#6b7280" fontSize={9} fontFamily="'DM Mono',monospace"
                    tickFormatter={v => `${v}a`} />
                  <YAxis stroke="#6b7280" fontSize={9} fontFamily="'DM Mono',monospace"
                    tickFormatter={v => fmt(v)} width={68} />
                  <Tooltip contentStyle={{ background: "#111318", border: "1px solid #23272f",
                    borderRadius: 8, fontFamily: "'DM Mono',monospace", fontSize: 10 }}
                    formatter={(v, n) => [fmtFull(v), n]}
                    labelFormatter={v => `Anio ${v} (edad ${edad + v})`} />
                  <Legend wrapperStyle={{ fontFamily: "'DM Mono',monospace", fontSize: 10 }} />
                  {cruzFondos.map(f => (
                    <Line key={f} type="monotone" dataKey={`Fondo ${f}`}
                      stroke={FONDO_COLORS[f]} strokeWidth={2.5} dot={false} />
                  ))}
                  {cruceData.cruces.map((c, i) => (
                    <ReferenceLine key={i} x={c.anio} stroke="#fbbf24" strokeDasharray="4 4" strokeWidth={1.5} />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>

            {cruceData.cruces.length > 0 ? (
              <div style={{ marginTop: 10, padding: 10, background: "#0a0c10", borderRadius: 7, border: "1px solid #fbbf2433" }}>
                <p style={{ fontFamily: "'DM Mono',monospace", fontSize: 11, color: "#fbbf24", margin: "0 0 4px", fontWeight: 600 }}>
                  Puntos de cruce:</p>
                {cruceData.cruces.map((c, i) => (
                  <p key={i} style={{ fontFamily: "'DM Mono',monospace", fontSize: 10, color: "#f3f4f6", margin: "2px 0" }}>
                    Anio {c.anio} (edad {edad + c.anio}): Fondo {c.gana} supera a
                    Fondo {c.gana === c.f1 ? c.f2 : c.f1} por {fmt(c.diff)}</p>
                ))}
              </div>
            ) : cruzFondos.length >= 2 && (
              <div style={{ marginTop: 10, padding: 10, background: "#0a0c10", borderRadius: 7, border: "1px solid #ef444433" }}>
                <p style={{ fontFamily: "'DM Mono',monospace", fontSize: 11, color: "#ef4444", margin: 0 }}>
                  Sin cruce en {aniosProy} anios. El fondo con mayor rentabilidad lidera desde el inicio.</p>
              </div>
            )}
          </div>

          {/* Escenarios */}
          <div style={P}>
            <h3 style={{ fontFamily: "'DM Mono',monospace", fontSize: 12, fontWeight: 700, margin: "0 0 8px" }}>
              Escenarios al anio {aniosProy} con {cruzAfp}</h3>
            <div style={{ display: "grid",
              gridTemplateColumns: `repeat(${Math.min(cruzFondos.length, 3)}, 1fr)`, gap: 8 }}>
              {escenarios.map(({ fondo, sc }) => (
                <div key={fondo} style={{ background: "#0a0c10", borderRadius: 7, padding: 10,
                  border: `1px solid ${FONDO_COLORS[fondo]}22` }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 5, marginBottom: 6 }}>
                    <span style={{ fontFamily: "'DM Mono',monospace", fontSize: 13, fontWeight: 700,
                      color: FONDO_COLORS[fondo] }}>Fondo {fondo}</span>
                    <span style={{ fontFamily: "'DM Mono',monospace", fontSize: 8, color: "#6b7280" }}>
                      {FONDO_RISK[fondo]}</span>
                  </div>
                  {sc.map(s => (
                    <div key={s.name} style={{ display: "flex", justifyContent: "space-between",
                      padding: "4px 0", borderBottom: "1px solid #1f2937" }}>
                      <span style={{ fontFamily: "'DM Mono',monospace", fontSize: 10, color: "#6b7280" }}>
                        {s.name} ({s.rent.toFixed(1)}%)</span>
                      <span style={{ fontFamily: "'DM Mono',monospace", fontSize: 10, fontWeight: 600, color: "#f3f4f6" }}>
                        {fmt(s.final)}</span>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>
        </>)}

        {/* ==================== ACUMULADO ==================== */}
        {tab === "acumulado" && (<>
          <div style={P}>
            <h2 style={{ fontFamily: "'DM Mono',monospace", fontSize: 15, fontWeight: 700, margin: "0 0 3px" }}>
              Acumulado historico {histStart}-{histEnd}</h2>
            <p style={{ fontFamily: "'DM Mono',monospace", fontSize: 10, color: "#6b7280", margin: "0 0 8px" }}>
              Simula haber estado en cada AFP+fondo durante el periodo.
              {datosReales.pct < 100 && (
                <span style={{ color: "#f97316" }}>
                  {" "}Los anios sin datos usan el promedio SP como fallback ({datosReales.reales}/{datosReales.total} celdas con datos reales = {datosReales.pct}%).
                </span>
              )}
            </p>
            <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
              <div><label style={L}>Desde</label>
                <select value={histStart} onChange={e => setHistStart(Number(e.target.value))}
                  style={{ ...I, width: 82, padding: "5px 6px", fontSize: 12 }}>
                  {allYears.map(y => <option key={y} value={y}>{y}</option>)}
                </select></div>
              <div><label style={L}>Hasta</label>
                <select value={histEnd} onChange={e => setHistEnd(Number(e.target.value))}
                  style={{ ...I, width: 82, padding: "5px 6px", fontSize: 12 }}>
                  {allYears.filter(y => y >= histStart).map(y => <option key={y} value={y}>{y}</option>)}
                </select></div>
              <span style={{ fontFamily: "'DM Mono',monospace", fontSize: 11, color: "#60a5fa", marginTop: 14 }}>
                = {histEnd - histStart + 1} anios</span>
            </div>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
            {currentList.slice(0, 15).map((item, idx) => (
              <RankRow key={`${item.afp}-${item.fondo}`} item={item} idx={idx} best={best} />
            ))}
          </div>
          {currentList.length > 15 && (
            <details style={{ marginTop: 6 }}>
              <summary style={{ color: "#60a5fa", cursor: "pointer", fontFamily: "'DM Mono',monospace", fontSize: 11 }}>
                Ver todo ({currentList.length})</summary>
              <div style={{ display: "flex", flexDirection: "column", gap: 2, marginTop: 4 }}>
                {currentList.slice(15).map((item, idx) => (
                  <RankRow key={`${item.afp}-${item.fondo}`} item={item} idx={idx + 15} best={best} />
                ))}
              </div>
            </details>
          )}
        </>)}

        {/* ==================== DATOS ==================== */}
        {tab === "datos" && (<>
          <div style={P}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 10, flexWrap: "wrap", gap: 6 }}>
              <div>
                <h2 style={{ fontFamily: "'DM Mono',monospace", fontSize: 15, fontWeight: 700, margin: 0 }}>
                  Datos historicos anuales</h2>
                <p style={{ fontFamily: "'DM Mono',monospace", fontSize: 10, color: "#6b7280", margin: "2px 0 0" }}>
                  Rentabilidad real anual promedio del sistema (%). null = sin dato, usa promedio SP.
                </p>
              </div>
              <button onClick={() => setEditingHist(!editingHist)} style={{
                padding: "5px 12px", borderRadius: 6, cursor: "pointer",
                fontFamily: "'DM Mono',monospace", fontSize: 11, fontWeight: 600,
                border: editingHist ? "1px solid #22c55e" : "1px solid #3b82f6",
                background: editingHist ? "#22c55e18" : "#3b82f618",
                color: editingHist ? "#22c55e" : "#60a5fa",
              }}>{editingHist ? "Listo" : "Editar datos"}</button>
            </div>

            {/* Grafico */}
            {histChartData.length > 0 && (
              <div style={{ width: "100%", height: 250, marginBottom: 12 }}>
                <ResponsiveContainer>
                  <AreaChart data={histChartData} margin={{ top: 6, right: 12, bottom: 6, left: 6 }}>
                    <XAxis dataKey="anio" stroke="#6b7280" fontSize={9} fontFamily="'DM Mono',monospace" />
                    <YAxis stroke="#6b7280" fontSize={9} fontFamily="'DM Mono',monospace" tickFormatter={v => `${v}%`} />
                    <Tooltip contentStyle={{ background: "#111318", border: "1px solid #23272f",
                      borderRadius: 8, fontFamily: "'DM Mono',monospace", fontSize: 10 }}
                      formatter={(v, n) => [v != null ? `${v.toFixed(2)}%` : "sin dato", n]} />
                    <Legend wrapperStyle={{ fontFamily: "'DM Mono',monospace", fontSize: 10 }} />
                    <ReferenceLine y={0} stroke="#6b728055" strokeDasharray="3 3" />
                    {FONDOS.map(f => (
                      <Area key={f} type="monotone" dataKey={`Fondo ${f}`}
                        stroke={FONDO_COLORS[f]} fill={FONDO_COLORS[f] + "18"}
                        strokeWidth={1.5} dot={false} connectNulls={false} />
                    ))}
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Tabla editable */}
            <div style={{ overflowX: "auto" }}>
              <table style={{ borderCollapse: "collapse", width: "100%", fontSize: 10, fontFamily: "'DM Mono',monospace" }}>
                <thead>
                  <tr>
                    <th style={thS}>Anio</th>
                    {FONDOS.map(f => <th key={f} style={{ ...thS, color: FONDO_COLORS[f] }}>F.{f}</th>)}
                    <th style={thS}>Fuente</th>
                  </tr>
                </thead>
                <tbody>
                  {allYears.map(y => (
                    <tr key={y} style={{ background: historico[y]?.src === "pendiente" ? "#f9731605" : "transparent" }}>
                      <td style={tdS}>{y}</td>
                      {FONDOS.map(f => {
                        const v = historico[y]?.[f];
                        return <td key={f} style={tdS}>
                          {editingHist ? (
                            <input type="number" step="0.01"
                              value={v != null ? v : ""}
                              placeholder="null"
                              onChange={e => updateHistCell(y, f, e.target.value)}
                              style={{ width: 62, background: "#0a0c10", border: "1px solid #23272f",
                                color: "#f3f4f6", borderRadius: 4, padding: "2px 4px", fontSize: 10,
                                fontFamily: "'DM Mono',monospace", outline: "none" }} />
                          ) : (
                            <span style={{ color: v == null ? "#374151" : v >= 0 ? "#22c55e" : "#ef4444" }}>
                              {v != null ? `${v > 0 ? "+" : ""}${v.toFixed(1)}%` : "null"}
                            </span>
                          )}
                        </td>;
                      })}
                      <td style={{ ...tdS, fontSize: 8,
                        color: historico[y]?.src === "pendiente" ? "#f97316" :
                               historico[y]?.src === "manual" ? "#a78bfa" : "#4b5563" }}>
                        {historico[y]?.src || ""}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div style={{ marginTop: 10, padding: 10, background: "#0a0c10", borderRadius: 7, border: "1px solid #3b82f622" }}>
              <p style={{ fontFamily: "'DM Mono',monospace", fontSize: 10, color: "#60a5fa", margin: "0 0 4px", fontWeight: 600 }}>
                Como obtener los datos faltantes:</p>
              <ol style={{ fontFamily: "'DM Mono',monospace", fontSize: 10, color: "#9ca3af", margin: 0,
                paddingLeft: 16, lineHeight: 1.8 }}>
                <li>Ir a spensiones.cl {">"} Informes {">"} Fondos de Pensiones {">"} Rentabilidad Mensual</li>
                <li>Abrir el informe de diciembre de cada anio</li>
                <li>Buscar la tabla "Rentabilidad Real de los Fondos de Pensiones" (12 meses)</li>
                <li>Tomar la fila "Promedio del Sistema" para cada fondo</li>
                <li>Click "Editar datos" arriba e ingresar los valores</li>
              </ol>
            </div>
          </div>
        </>)}

        {/* ==================== COMPARTIR ==================== */}
        {tab === "compartir" && (
          <div style={P}>
            <h2 style={{ fontFamily: "'DM Mono',monospace", fontSize: 15, fontWeight: 700, margin: "0 0 10px" }}>
              Como compartir esta herramienta</h2>

            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              <div style={{ padding: 12, background: "#0a0c10", borderRadius: 8, border: "1px solid #22c55e22" }}>
                <h3 style={{ fontFamily: "'DM Mono',monospace", fontSize: 12, color: "#22c55e", margin: "0 0 6px", fontWeight: 600 }}>
                  Opcion 1: Mandar el link de este chat</h3>
                <p style={{ fontFamily: "'DM Mono',monospace", fontSize: 10, color: "#9ca3af", margin: 0, lineHeight: 1.6 }}>
                  Si estas viendo esto en claude.ai, puedes compartir el artifact directamente
                  haciendo click en el boton de compartir del artifact.
                </p>
              </div>

              <div style={{ padding: 12, background: "#0a0c10", borderRadius: 8, border: "1px solid #3b82f622" }}>
                <h3 style={{ fontFamily: "'DM Mono',monospace", fontSize: 12, color: "#60a5fa", margin: "0 0 6px", fontWeight: 600 }}>
                  Opcion 2: Web gratuita en Vercel (5 minutos)</h3>
                <ol style={{ fontFamily: "'DM Mono',monospace", fontSize: 10, color: "#9ca3af", margin: 0,
                  paddingLeft: 16, lineHeight: 2 }}>
                  <li>Instala Node.js si no lo tienes (nodejs.org)</li>
                  <li>npx create-react-app afp-evaluador</li>
                  <li>cd afp-evaluador</li>
                  <li>npm install recharts</li>
                  <li>Reemplaza src/App.js con el codigo de este artifact</li>
                  <li>npm run build</li>
                  <li>Sube a vercel.com (gratis) o netlify.com (gratis)</li>
                  <li>Comparte el link</li>
                </ol>
              </div>

              <div style={{ padding: 12, background: "#0a0c10", borderRadius: 8, border: "1px solid #c084fc22" }}>
                <h3 style={{ fontFamily: "'DM Mono',monospace", fontSize: 12, color: "#c084fc", margin: "0 0 6px", fontWeight: 600 }}>
                  Opcion 3: GitHub Pages (gratis, mas tecnico)</h3>
                <ol style={{ fontFamily: "'DM Mono',monospace", fontSize: 10, color: "#9ca3af", margin: 0,
                  paddingLeft: 16, lineHeight: 2 }}>
                  <li>Crea un repo en github.com</li>
                  <li>Sube el proyecto con npm run build</li>
                  <li>Activa GitHub Pages en Settings</li>
                  <li>URL gratuita: tunombre.github.io/afp-evaluador</li>
                </ol>
              </div>

              <div style={{ padding: 12, background: "#0a0c10", borderRadius: 8, border: "1px solid #f9731622" }}>
                <h3 style={{ fontFamily: "'DM Mono',monospace", fontSize: 12, color: "#f97316", margin: "0 0 6px", fontWeight: 600 }}>
                  Opcion 4: Solo HTML (sin instalar nada)</h3>
                <p style={{ fontFamily: "'DM Mono',monospace", fontSize: 10, color: "#9ca3af", margin: 0, lineHeight: 1.6 }}>
                  Pideme que convierta esto a un archivo .html autocontenido con React y Recharts
                  cargados desde CDN. Lo abres directo en el navegador o lo subes a cualquier hosting estatico.
                  Es la opcion mas simple para compartir.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* FOOTER */}
        <div style={{ ...P, marginTop: 14, border: "1px solid #c084fc22" }}>
          <h3 style={{ fontFamily: "'DM Mono',monospace", fontSize: 11, fontWeight: 700, color: "#c084fc", margin: "0 0 5px" }}>
            Metodologia</h3>
          <div style={{ fontFamily: "'DM Mono',monospace", fontSize: 10, color: "#9ca3af", lineHeight: 1.7 }}>
            <p style={{ margin: "0 0 5px" }}>
              Las <strong style={{color:"#f3f4f6"}}>proyecciones</strong> usan los promedios reales confirmados por la SP
              (Fondo A: {PROMEDIO_SP_CONFIRMADO.A}%, ..., E: {PROMEDIO_SP_CONFIRMADO.E}%), identicos para todas las AFPs.
              Lo que diferencia una AFP de otra en la proyeccion es unicamente la comision.
            </p>
            <p style={{ margin: "0 0 5px" }}>
              El <strong style={{color:"#f3f4f6"}}>acumulado historico</strong> usa datos anuales reales donde los hay,
              y el promedio SP como fallback donde faltan. El % de datos reales se muestra en pantalla.
            </p>
            <p style={{ margin: 0 }}>
              Con los promedios confirmados, el Fondo A ({PROMEDIO_SP_CONFIRMADO.A}%) tiene ~1.9 puntos porcentuales
              mas que el D ({PROMEDIO_SP_CONFIRMADO.D}%). Esa diferencia compuesta a 30 anios es enorme.
              Pero el A tuvo anios de -29% (2008) y el D nunca bajo de -8%.
              La comision es la unica variable que controlas con certeza.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

const thS = { padding: "3px 4px", borderBottom: "1px solid #374151", textAlign: "left",
  color: "#9ca3af", fontWeight: 600, fontSize: 9 };
const tdS = { padding: "2px 4px", borderBottom: "1px solid #1f2937", fontSize: 10 };
