import "./App.css";
import { useState, useEffect, useRef } from "react";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const ASSET_TV = {
  // Regular markets
  "EUR/USD": "FX:EURUSD", "GBP/USD": "FX:GBPUSD", "AUD/USD": "FX:AUDUSD",
  "USD/JPY": "FX:USDJPY", "USD/CAD": "FX:USDCAD", "USD/CHF": "FX:USDCHF",
  "EUR/GBP": "FX:EURGBP", "EUR/JPY": "FX:EURJPY", "EUR/CHF": "FX:EURCHF",
  "EUR/AUD": "FX:EURAUD", "EUR/CAD": "FX:EURCAD", "GBP/JPY": "FX:GBPJPY",
  "GBP/CHF": "FX:GBPCHF", "GBP/AUD": "FX:GBPAUD", "GBP/CAD": "FX:GBPCAD",
  "AUD/JPY": "FX:AUDJPY", "AUD/CAD": "FX:AUDCAD", "AUD/CHF": "FX:AUDCHF",
  "CAD/JPY": "FX:CADJPY", "CAD/CHF": "FX:CADCHF", "CHF/JPY": "FX:CHFJPY",
  "NZD/USD": "FX:NZDUSD", "NZD/JPY": "FX:NZDJPY", "NZD/CAD": "FX:NZDCAD",
  "NZD/CHF": "FX:NZDCHF", "NZD/GBP": "FX:NZDGBP",
  "Bitcoin": "BINANCE:BTCUSDT", "Ethereum": "BINANCE:ETHUSDT",
  "Dash": "BINANCE:DASHUSDT", "Chainlink": "BINANCE:LINKUSDT",
  "Bitcoin Cash": "BINANCE:BCHUSDT",
  "Apple": "NASDAQ:AAPL", "Microsoft": "NASDAQ:MSFT", "Tesla": "NASDAQ:TSLA",
  "Netflix": "NASDAQ:NFLX", "Amazon": "NASDAQ:AMZN", "Google": "NASDAQ:GOOGL",
  "Meta": "NASDAQ:META", "Intel": "NASDAQ:INTC", "Cisco": "NASDAQ:CSCO",
  "ExxonMobil": "NYSE:XOM", "Johnson & Johnson": "NYSE:JNJ", "Pfizer": "NYSE:PFE",
  "Boeing": "NYSE:BA", "McDonald's": "NYSE:MCD", "JPMorgan": "NYSE:JPM",
  "American Express": "NYSE:AXP", "Citigroup": "NYSE:C", "Alibaba": "NYSE:BABA",
  "US100": "NASDAQ:NDX", "SP500": "SP:SPX", "DJI30": "DJ:DJI",
  "DAX": "XETR:DAX", "FTSE 100": "LSE:UKX", "CAC 40": "EURONEXT:PX1",
  "Nikkei 225": "TVC:NI225", "AUS 200": "TVC:AS51",
  "Euro Stoxx 50": "TVC:SX5E", "Hang Seng": "TVC:HSI",
  "Gold": "TVC:GOLD", "Silver": "TVC:SILVER", "Oil Brent": "TVC:UKOIL",
  "Oil WTI": "TVC:USOIL", "Natural Gas": "TVC:NATURALGAS", "Platinum": "TVC:PLATINUM",
  // OTC Forex — TradingView proxy charts
  "EUR/USD OTC": "FX:EURUSD", "GBP/USD OTC": "FX:GBPUSD",
  "AUD/USD OTC": "FX:AUDUSD", "USD/JPY OTC": "FX:USDJPY",
  "USD/CAD OTC": "FX:USDCAD", "USD/CHF OTC": "FX:USDCHF",
  "EUR/GBP OTC": "FX:EURGBP", "EUR/JPY OTC": "FX:EURJPY",
  "GBP/JPY OTC": "FX:GBPJPY",
  // Deriv synthetics — no TradingView chart (null = show placeholder)
  "Volatility 10": null, "Volatility 25": null, "Volatility 50": null,
  "Volatility 75": null, "Volatility 100": null,
  "Boom 500": null, "Boom 1000": null,
  "Crash 500": null, "Crash 1000": null,
};

// Assets that are OTC (no real market, broker/synthetic pricing)
const OTC_ASSETS = new Set([
  "EUR/USD OTC","GBP/USD OTC","AUD/USD OTC","USD/JPY OTC","USD/CAD OTC",
  "USD/CHF OTC","EUR/GBP OTC","EUR/JPY OTC","GBP/JPY OTC",
  "Volatility 10","Volatility 25","Volatility 50","Volatility 75","Volatility 100",
  "Boom 500","Boom 1000","Crash 500","Crash 1000",
]);

const CATEGORIES = {
  "Форекс":     ["EUR/USD","GBP/USD","AUD/USD","USD/JPY","USD/CAD","USD/CHF","EUR/GBP","EUR/JPY","EUR/CHF","EUR/AUD","EUR/CAD","GBP/JPY","GBP/CHF","GBP/AUD","GBP/CAD","AUD/JPY","AUD/CAD","AUD/CHF","CAD/JPY","CAD/CHF","CHF/JPY","NZD/USD","NZD/JPY","NZD/CAD","NZD/CHF","NZD/GBP"],
  "Крипто":     ["Bitcoin","Ethereum","Dash","Chainlink","Bitcoin Cash"],
  "Акции":      ["Apple","Microsoft","Tesla","Netflix","Amazon","Google","Meta","Intel","Cisco","ExxonMobil","Johnson & Johnson","Pfizer","Boeing","McDonald's","JPMorgan","American Express","Citigroup","Alibaba"],
  "Индексы":    ["US100","SP500","DJI30","DAX","FTSE 100","CAC 40","Nikkei 225","AUS 200","Euro Stoxx 50","Hang Seng"],
  "Товары":     ["Gold","Silver","Oil Brent","Oil WTI","Natural Gas","Platinum"],
};

const TIMEFRAMES = [
  { label: "1м", value: "M1" },
  { label: "3м", value: "M3" },
  { label: "5м", value: "M5" },
  { label: "15м", value: "M15" },
];

const MODES = ["Новичок", "Уверенный", "Про"];

const C = {
  bg: "#0a0e1a",
  card: "#111827",
  card2: "#1a2235",
  input: "#0d1424",
  primary: "#3b82f6",
  green: "#10b981",
  red: "#ef4444",
  orange: "#f97316",
  purple: "#a78bfa",
  text: "#f1f5f9",
  muted: "#64748b",
  border: "rgba(255,255,255,0.07)",
};

const TF_MINS = { M1: 1, M3: 3, M5: 5, M15: 15 };

function genTradeId() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
}

function getAssetCurrencies(sym) {
  const clean = sym.replace(" OTC", "");
  const parts = clean.split("/");
  if (parts.length === 2 && parts[0].length >= 3 && parts[1].length >= 3) {
    return [parts[0], parts[1]];
  }
  const usdList = ["Gold","Silver","Oil Brent","Oil WTI","Natural Gas","Platinum",
    "US100","SP500","DJI30","Apple","Microsoft","Tesla","Netflix","Amazon","Google",
    "Meta","Intel","Cisco","ExxonMobil","Johnson & Johnson","Pfizer","Boeing",
    "McDonald's","JPMorgan","American Express","Citigroup","Alibaba"];
  if (usdList.includes(sym)) return ["USD"];
  if (["DAX","CAC 40","Euro Stoxx 50"].includes(sym)) return ["EUR"];
  if (sym === "FTSE 100") return ["GBP"];
  if (sym === "Nikkei 225") return ["JPY"];
  if (sym === "AUS 200") return ["AUD"];
  return [];
}

// ─── TradingView chart ────────────────────────────────────────────────────────
function TradingViewWidget({ symbol, interval }) {
  const id = "tv-widget-container";
  useEffect(() => {
    const el = document.getElementById(id);
    if (!el) return;
    el.innerHTML = "";
    const s = document.createElement("script");
    s.src = "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";
    s.async = true;
    s.innerHTML = JSON.stringify({
      autosize: true, symbol, timezone: "Etc/UTC", theme: "dark", style: "1",
      locale: "ru", enable_publishing: false, hide_top_toolbar: false,
      hide_legend: true, save_image: false, container_id: id,
      interval: interval === "M1" ? "1" : interval === "M3" ? "3" : interval === "M5" ? "5" : "15",
    });
    el.appendChild(s);
  }, [symbol, interval]);
  return (
    <div style={{ height: "300px", width: "100%", borderRadius: "16px", overflow: "hidden", background: C.card }}>
      <div id={id} style={{ height: "100%", width: "100%" }} />
    </div>
  );
}

// ─── Countdown bar ────────────────────────────────────────────────────────────
function CountdownBar({ expiryTime, totalMins, onExpire }) {
  const totalSecs = totalMins * 60;
  const [remaining, setRemaining] = useState(totalSecs);
  const firedRef = useRef(false);

  useEffect(() => {
    if (!expiryTime) return;
    firedRef.current = false;
    const tick = () => {
      const diff = Math.max(0, Math.round((new Date(expiryTime) - Date.now()) / 1000));
      setRemaining(diff);
      if (diff === 0 && !firedRef.current) {
        firedRef.current = true;
        onExpire?.();
      }
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [expiryTime]);

  const pct = totalSecs > 0 ? (remaining / totalSecs) * 100 : 0;
  const m = String(Math.floor(remaining / 60)).padStart(2, "0");
  const s = String(remaining % 60).padStart(2, "0");

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
        <span style={{ color: C.muted, fontSize: "12px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.6px" }}>
          ⏱ До истечения
        </span>
        <span style={{ color: remaining < 30 ? C.red : C.text, fontSize: "14px", fontWeight: 700, fontVariantNumeric: "tabular-nums" }}>
          {m}:{s}
        </span>
      </div>
      <div style={{ width: "100%", height: "6px", borderRadius: "999px", background: "rgba(255,255,255,0.06)", overflow: "hidden" }}>
        <div style={{
          height: "100%", width: pct + "%", borderRadius: "999px",
          background: pct > 40
            ? `linear-gradient(90deg, ${C.primary}, ${C.green})`
            : `linear-gradient(90deg, ${C.red}, ${C.orange})`,
          transition: "width 1s linear",
        }} />
      </div>
    </div>
  );
}

// ─── Trade history card ───────────────────────────────────────────────────────
function TradeCard({ trade }) {
  if (!trade.signal || trade.signal === "NO SIGNAL") return null;
  const result = trade.result || "PENDING";
  const resultColor = result === "WIN" ? C.green : result === "LOSS" ? C.red : C.muted;
  const resultText  = result === "WIN" ? "✅ Выиграл" : result === "LOSS" ? "❌ Проиграл" : "⏳ Ожидает";
  const modeColor   = trade.mode === "ai_scanner" ? C.purple : C.primary;
  const modeLabel   = trade.mode === "ai_scanner" ? "AI СКАНЕР" : "РУЧНОЙ";
  const sigColor    = trade.signal === "UP" ? C.green : C.red;
  const ts = trade.timestamp
    ? new Date(trade.timestamp.endsWith("Z") ? trade.timestamp : trade.timestamp + "Z")
        .toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" })
    : "";

  return (
    <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: "14px", padding: "14px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "8px" }}>
        <div style={{ display: "flex", gap: "5px", flexWrap: "wrap" }}>
          <span style={{ background: modeColor + "20", color: modeColor, padding: "2px 8px", borderRadius: "5px", fontSize: "10px", fontWeight: 700 }}>
            {modeLabel}
          </span>
          {trade.is_otc && (
            <span style={{ background: "rgba(245,158,11,0.15)", color: "#f59e0b", padding: "2px 8px", borderRadius: "5px", fontSize: "10px", fontWeight: 700 }}>
              OTC
            </span>
          )}
          {trade.is_martingale && (
            <span style={{ background: "rgba(249,115,22,0.15)", color: C.orange, padding: "2px 8px", borderRadius: "5px", fontSize: "10px", fontWeight: 700 }}>
              ДОГОН {trade.martingale_step}/3
            </span>
          )}
        </div>
        <span style={{ color: resultColor, fontSize: "13px", fontWeight: 700 }}>{resultText}</span>
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <span style={{ color: C.text, fontWeight: 700, fontSize: "14px" }}>{trade.symbol}</span>
          <span style={{ color: C.muted, fontSize: "12px", marginLeft: "6px" }}>{trade.timeframe}</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span style={{ color: sigColor, fontWeight: 800, fontSize: "14px" }}>
            {trade.signal === "UP" ? "ВВЕРХ ⬆" : "ВНИЗ ⬇"}
          </span>
          <span style={{ color: sigColor, fontSize: "13px" }}>{trade.confidence}%</span>
        </div>
      </div>
      {(trade.entry_price || ts) && (
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: "6px" }}>
          {trade.entry_price ? (
            <span style={{ color: C.muted, fontSize: "11px" }}>
              Вход: {Number(trade.entry_price).toLocaleString("ru-RU", { maximumFractionDigits: 5 })}
            </span>
          ) : <span />}
          {ts && <span style={{ color: C.muted, fontSize: "11px" }}>{ts}</span>}
        </div>
      )}
    </div>
  );
}

// ─── News event card ──────────────────────────────────────────────────────────
function NewsEventCard({ event }) {
  const impactIcon  = event.impact === "high" ? "🔴" : event.impact === "medium" ? "🟡" : "⚪";
  const impactColor = event.impact === "high" ? C.red  : event.impact === "medium" ? "#f59e0b" : C.muted;
  const timeStr = event.time_utc
    ? new Date(event.time_utc).toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" })
    : "";
  const m = event.minutes_until;
  const timeLabel = m === null ? "" : m < 0 ? "прошло" : m === 0 ? "СЕЙЧАС!" : `через ${m}м`;
  const urgentColor = m !== null && m >= 0 && m <= 30 ? impactColor : C.muted;

  return (
    <div style={{ background: C.card, border: `1px solid ${event.impact !== "low" ? impactColor + "30" : C.border}`, borderRadius: "12px", padding: "12px 14px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ display: "flex", gap: "7px", alignItems: "center" }}>
          <span>{impactIcon}</span>
          <span style={{ background: impactColor + "25", color: impactColor, border: `1px solid ${impactColor}40`, padding: "1px 7px", borderRadius: "4px", fontSize: "11px", fontWeight: 700 }}>
            {event.currency}
          </span>
          <span style={{ color: C.muted, fontSize: "12px" }}>{timeStr}</span>
        </div>
        {timeLabel && <span style={{ color: urgentColor, fontSize: "11px", fontWeight: 700 }}>{timeLabel}</span>}
      </div>
      <div style={{ color: C.text, fontSize: "13px", fontWeight: 600, marginTop: "6px", paddingLeft: "24px" }}>
        {event.title}
      </div>
      {(event.forecast || event.previous || event.actual) && (
        <div style={{ display: "flex", gap: "14px", marginTop: "5px", paddingLeft: "24px", flexWrap: "wrap" }}>
          {event.forecast && <span style={{ color: C.muted, fontSize: "11px" }}>Прогноз: <strong style={{ color: C.text }}>{event.forecast}</strong></span>}
          {event.previous && <span style={{ color: C.muted, fontSize: "11px" }}>Пред: <strong style={{ color: C.text }}>{event.previous}</strong></span>}
          {event.actual   && <span style={{ color: C.muted, fontSize: "11px" }}>Факт: <strong style={{ color: C.green }}>{event.actual}</strong></span>}
        </div>
      )}
    </div>
  );
}

// ─── Details panel ────────────────────────────────────────────────────────────
function DetailsPanel({ data, signalData }) {
  const sr    = data.support_resistance || {};
  const fib   = data.fibonacci || {};
  const trend = data.trend || {};
  const cp    = data.chart_pattern || {};
  const er    = data.entry_recommendation || {};
  const currentPrice = signalData?.entry_price;

  const trendIcon = trend.direction === "up" ? "↗️" : trend.direction === "down" ? "↘️" : "↔️";
  const trendLabel = trend.direction === "up" ? "Восходящий" : trend.direction === "down" ? "Нисходящий" : "Боковик";
  const strengthLabel = trend.strength === "strong" ? "сильный" : trend.strength === "moderate" ? "умеренный" : "слабый";
  const cpIcon = cp.pattern_type === "bullish" ? "🔵" : cp.pattern_type === "bearish" ? "🔴" : "⚪";
  const riskColor = er.risk_level === "низкий" ? C.green : er.risk_level === "высокий" ? C.red : "#f59e0b";

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
      {/* Trend + Pattern */}
      <div style={{ background: C.input, borderRadius: "10px", padding: "10px 12px", border: `1px solid ${C.border}` }}>
        <div style={{ color: C.muted, fontSize: "10px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.6px", marginBottom: "6px" }}>📊 Технический анализ</div>
        <div style={{ fontSize: "12px", color: "#c8d0e0", lineHeight: "1.8" }}>
          <div>Тренд: {trendIcon} {trendLabel} ({strengthLabel}, ADX: {trend.adx_value})</div>
          {cp.pattern_name && <div>{cpIcon} Фигура: {cp.pattern_name} ({cp.confidence}%)</div>}
        </div>
      </div>

      {/* Levels */}
      {(sr.resistance_levels?.length > 0 || sr.support_levels?.length > 0) && (
        <div style={{ background: C.input, borderRadius: "10px", padding: "10px 12px", border: `1px solid ${C.border}` }}>
          <div style={{ color: C.muted, fontSize: "10px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.6px", marginBottom: "6px" }}>📍 Ключевые уровни</div>
          <div style={{ fontSize: "12px", lineHeight: "1.9" }}>
            {sr.resistance_levels?.slice(0,3).map((r,i) => (
              <div key={i} style={{ color: C.red }}>🔴 Сопр: {r.toLocaleString("ru-RU",{maximumFractionDigits:5})}</div>
            ))}
            {currentPrice && <div style={{ color: C.primary }}>▶ Текущая: {Number(currentPrice).toLocaleString("ru-RU",{maximumFractionDigits:5})}</div>}
            {sr.support_levels?.slice(0,3).map((s,i) => (
              <div key={i} style={{ color: C.green }}>🟢 Подд: {s.toLocaleString("ru-RU",{maximumFractionDigits:5})}</div>
            ))}
          </div>
        </div>
      )}

      {/* Fibonacci */}
      {fib.nearest_level_name && (
        <div style={{ background: C.input, borderRadius: "10px", padding: "10px 12px", border: `1px solid ${C.border}` }}>
          <div style={{ color: C.muted, fontSize: "10px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.6px", marginBottom: "4px" }}>📐 Фибоначчи</div>
          <div style={{ fontSize: "12px", color: "#c8d0e0" }}>
            Ближайший уровень: <strong style={{ color: C.purple }}>{fib.nearest_level_name}</strong> = {fib.nearest_level_price?.toLocaleString("ru-RU",{maximumFractionDigits:5})}
          </div>
        </div>
      )}

      {/* Entry recommendation */}
      {er.entry_zone && (
        <div style={{ background: C.input, borderRadius: "10px", padding: "10px 12px", border: `1px solid ${C.border}` }}>
          <div style={{ color: C.muted, fontSize: "10px", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.6px", marginBottom: "6px" }}>⚡ Точка входа</div>
          <div style={{ fontSize: "12px", color: "#c8d0e0", lineHeight: "1.8" }}>
            <div>Зона: <strong style={{ color: C.text }}>{er.entry_zone}</strong></div>
            {er.stop_zone && <div>Стоп: <strong style={{ color: C.red }}>{er.stop_zone}</strong></div>}
            <div>Риск: <strong style={{ color: riskColor }}>{er.risk_level === "низкий" ? "🟢 Низкий" : er.risk_level === "высокий" ? "🔴 Высокий" : "🟡 Средний"}</strong></div>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Main app ─────────────────────────────────────────────────────────────────
export default function App() {
  // Asset selection
  const [category, setCategory]   = useState("Форекс");
  const [symbol,   setSymbol]     = useState("EUR/USD");
  const [timeframe, setTimeframe] = useState("M1");
  const [mode,     setMode]       = useState("Уверенный");

  // Navigation
  const [activeTab, setActiveTab] = useState("signal");

  // Trade flow: idle → signal → confirmed → result_shown
  const [flowStep,    setFlowStep]    = useState("idle");
  const [signalData,  setSignalData]  = useState(null);
  const [detailsData, setDetailsData] = useState(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [tradeId,     setTradeId]     = useState(null);
  const [isScanner,   setIsScanner]   = useState(false);
  const [dogonStep,   setDogonStep]   = useState(0);
  const [sessionStopped, setSessionStopped] = useState(false);
  const [loading,     setLoading]     = useState(false);
  const [currentPrice, setCurrentPrice] = useState(null);
  const [winFlash,    setWinFlash]    = useState(false);

  // Scanner tab
  const [scanData,    setScanData]    = useState(null);
  const [scanLoading, setScanLoading] = useState(false);

  // History tab
  const [historyData, setHistoryData] = useState(null);
  const [historyModeFilter,   setHistoryModeFilter]   = useState("all");
  const [historyResultFilter, setHistoryResultFilter] = useState("all");
  const [historyPage,         setHistoryPage]         = useState(0);
  const [historyHasMore,      setHistoryHasMore]      = useState(false);

  // Session tab
  const [sessionData,     setSessionData]     = useState(null);
  const [sessionDeposit,  setSessionDeposit]  = useState("1000");
  const [sessionRisk,     setSessionRisk]     = useState("5");
  const [sessionMaxMart,  setSessionMaxMart]  = useState(3);
  const [sessionLoading,  setSessionLoading]  = useState(false);

  // News tab
  const [newsData,           setNewsData]           = useState(null);
  const [newsLoading,        setNewsLoading]         = useState(false);
  const [newsCurrencyFilter, setNewsCurrencyFilter]  = useState("ALL");
  const [newsImpactFilter,   setNewsImpactFilter]    = useState("all");
  const [newsIndicator,      setNewsIndicator]       = useState(null);
  const [newsWarning,        setNewsWarning]         = useState(null);

  // Reset symbol when category changes
  useEffect(() => {
    const list = CATEGORIES[category];
    if (list && !list.includes(symbol)) setSymbol(list[0]);
  }, [category]);

  // Load history when tab opens
  useEffect(() => {
    if (activeTab === "history") fetchHistory(true);
  }, [activeTab]);

  // Load session when tab opens
  useEffect(() => {
    if (activeTab === "session") fetchCurrentSession();
  }, [activeTab]);

  // News indicator — refresh when symbol changes
  useEffect(() => {
    let cancelled = false;
    async function checkIndicator() {
      try {
        const res = await fetch(`${API}/news/check?symbol=${encodeURIComponent(symbol)}`);
        const d   = await res.json();
        if (cancelled) return;
        if (!d.warning) { setNewsIndicator("green"); return; }
        setNewsIndicator(d.events.some(e => e.impact === "high") ? "red" : "yellow");
      } catch (_) { if (!cancelled) setNewsIndicator(null); }
    }
    checkIndicator();
    return () => { cancelled = true; };
  }, [symbol]);

  // News tab — load + auto-refresh every 5 min while tab is open
  useEffect(() => {
    if (activeTab !== "news") return;
    fetchNewsTab();
    const id = setInterval(fetchNewsTab, 5 * 60 * 1000);
    return () => clearInterval(id);
  }, [activeTab, newsCurrencyFilter]);

  // Poll live price while trade is confirmed (before timer fires)
  useEffect(() => {
    if (flowStep !== "confirmed") { setCurrentPrice(null); return; }
    const tradeSym = signalData?.symbol || symbol;
    const poll = async () => {
      try {
        const res = await fetch(`${API}/price?symbol=${encodeURIComponent(tradeSym)}`);
        const d   = await res.json();
        if (d.price) setCurrentPrice(d.price);
      } catch (_) {}
    };
    poll();
    const id = setInterval(poll, 5000);
    return () => clearInterval(id);
  }, [flowStep, signalData?.symbol, symbol]);

  // ── helpers ──────────────────────────────────────────────────────────────

  function playSound(type) {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const freqs = type === "win" ? [523, 659, 784] : [440, 550];
      freqs.forEach((freq, i) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain); gain.connect(ctx.destination);
        osc.frequency.value = freq; osc.type = "sine";
        const t = ctx.currentTime + i * 0.12;
        gain.gain.setValueAtTime(0.25, t);
        gain.gain.exponentialRampToValueAtTime(0.001, t + 0.35);
        osc.start(t); osc.stop(t + 0.35);
      });
    } catch (_) {}
  }

  async function fetchHistory(reset = true) {
    const page = reset ? 0 : historyPage;
    if (reset) setHistoryPage(0);
    try {
      const mode   = historyModeFilter   !== "all" ? `&mode=${historyModeFilter}`   : "";
      const result = historyResultFilter !== "all" ? `&result=${historyResultFilter}` : "";
      const res    = await fetch(`${API}/history?limit=20&offset=${page*20}${mode}${result}`);
      const d      = await res.json();
      if (reset) {
        setHistoryData(d);
      } else {
        setHistoryData(prev => prev ? {
          ...d,
          history: [...(prev.history || []), ...(d.history || [])],
        } : d);
      }
      setHistoryHasMore((d.history?.length || 0) >= 20);
      if (!reset) setHistoryPage(p => p + 1);
    } catch (_) {}
  }

  async function fetchCurrentSession() {
    try {
      const res = await fetch(`${API}/session/current`);
      const d   = await res.json();
      setSessionData(d.active === false ? null : d);
    } catch (_) {}
  }

  async function startSession() {
    setSessionLoading(true);
    try {
      await fetch(`${API}/session/start`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ deposit: parseFloat(sessionDeposit), risk_pct: parseFloat(sessionRisk), max_martingale: sessionMaxMart }),
      });
      await fetchCurrentSession();
    } catch (_) {} finally { setSessionLoading(false); }
  }

  async function endSession() {
    if (!sessionData?.id) return;
    setSessionLoading(true);
    try {
      await fetch(`${API}/session/end`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionData.id }),
      });
      setSessionData(null);
    } catch (_) {} finally { setSessionLoading(false); }
  }

  async function fetchNewsTab() {
    setNewsLoading(true);
    try {
      const url = newsCurrencyFilter === "ALL"
        ? `${API}/news`
        : `${API}/news?currency=${newsCurrencyFilter}`;
      const res = await fetch(url);
      setNewsData(await res.json());
    } catch (_) {} finally { setNewsLoading(false); }
  }

  async function postHistoryAdd(id, sig, expiry, scannerMode, step) {
    const sym = sig.symbol || symbol;
    const otc = OTC_ASSETS.has(sym);
    try {
      await fetch(`${API}/history/add`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          trade_id:        id,
          signal:          sig.signal,
          confidence:      sig.confidence,
          symbol:          sym,
          timeframe:       sig.timeframe || timeframe,
          mode_label:      scannerMode ? "ai_scanner" : "manual",
          is_martingale:   step > 0,
          martingale_step: step,
          entry_price:     sig.entry_price,
          expiry_time:     expiry,
          reasons:         sig.reasons || [],
          is_otc:          otc,
          market_type:     otc ? "otc" : "forex",
        }),
      });
    } catch (_) {}
  }

  async function postHistoryUpdate(id, result) {
    try {
      await fetch(`${API}/history/update`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ trade_id: id, result }),
      });
    } catch (_) {}
  }

  // ── flow actions ─────────────────────────────────────────────────────────

  async function fetchSignal(scannerMode = false, skipNewsCheck = false) {
    if (loading) return;

    // Check for upcoming high/medium impact news before fetching
    if (!skipNewsCheck) {
      try {
        const res = await fetch(`${API}/news/check?symbol=${encodeURIComponent(symbol)}`);
        const d   = await res.json();
        if (d.warning) {
          setNewsWarning({
            message:   d.warning_message,
            events:    d.events,
            onProceed: () => { setNewsWarning(null); fetchSignal(scannerMode, true); },
          });
          return;
        }
      } catch (_) {} // silently skip news check on network error
    }

    setLoading(true);
    setIsScanner(scannerMode);
    try {
      const res  = await fetch(`${API}/signal`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol, timeframe, mode }),
      });
      const data = await res.json();
      setSignalData(data);
      setFlowStep("signal");
      if (data.signal === "UP" || data.signal === "DOWN") playSound("signal");
      // Kick off detailed analysis in background for real signals
      if (data.signal === "UP" || data.signal === "DOWN") {
        setDetailsData(null);
        setDetailsLoading(true);
        fetch(`${API}/signal/details`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ symbol, timeframe, mode }),
        }).then(r => r.json()).then(d => { setDetailsData(d); setDetailsLoading(false); })
          .catch(() => setDetailsLoading(false));
      }
    } catch (_) {
      setSignalData({
        signal: "ERROR", confidence: 0,
        reasons: ["Ошибка подключения к серверу"],
        entry_price: null, symbol, timeframe,
        expiry_time: new Date(Date.now() + 60000).toISOString(),
      });
      setFlowStep("signal");
    } finally {
      setLoading(false);
    }
  }

  async function handleConfirmEntry() {
    const id     = genTradeId();
    const mins   = TF_MINS[signalData?.timeframe || timeframe] || 1;
    const expiry = new Date(Date.now() + mins * 60000).toISOString();
    setTradeId(id);
    await postHistoryAdd(id, signalData, expiry, isScanner, dogonStep);
    setSignalData(prev => ({ ...prev, expiry_time: expiry }));
    setFlowStep("confirmed");
  }

  function handleSkip() {
    setDetailsData(null);
    setDetailsLoading(false);
    setSignalData(null);
    setFlowStep("idle");
  }

  function handleTimerExpire() {
    setFlowStep("result_shown");
  }

  async function handleWin() {
    if (tradeId) await postHistoryUpdate(tradeId, "WIN");
    playSound("win");
    setWinFlash(true);
    setTimeout(() => setWinFlash(false), 1800);
    setDogonStep(0);
    setSessionStopped(false);
    setDetailsData(null);
    setDetailsLoading(false);
    setSignalData(null);
    setTradeId(null);
    setFlowStep("idle");
  }

  async function handleLoss() {
    if (tradeId) await postHistoryUpdate(tradeId, "LOSS");
    const next = dogonStep + 1;
    setDetailsData(null);
    setDetailsLoading(false);
    setTradeId(null);
    setSignalData(null);
    if (next > 3) {
      setDogonStep(0);
      setSessionStopped(true);
      setFlowStep("idle");
    } else {
      setDogonStep(next);
      setFlowStep("idle");
      setTimeout(() => fetchSignal(isScanner), 300);
    }
  }

  function resetSession() {
    setDogonStep(0);
    setSessionStopped(false);
    setDetailsData(null);
    setDetailsLoading(false);
    setSignalData(null);
    setTradeId(null);
    setFlowStep("idle");
  }

  // ── scanner actions ───────────────────────────────────────────────────────

  async function fetchScan() {
    setScanLoading(true);
    setScanData(null);
    try {
      const res  = await fetch(`${API}/scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol, timeframe: "M1", mode }),
      });
      setScanData(await res.json());
    } catch (_) {
      setScanData({ results: [], best: null, reason: "Ошибка подключения к серверу" });
    } finally {
      setScanLoading(false);
    }
  }

  async function handleScannerConfirm(best) {
    const id       = genTradeId();
    const mins     = TF_MINS[best.timeframe] || 1;
    const expiry   = new Date(Date.now() + mins * 60000).toISOString();
    const synthetic = {
      signal: best.signal, confidence: best.confidence,
      reasons: best.reasons || [], entry_price: best.entry_price,
      symbol, timeframe: best.timeframe, expiry_time: expiry,
    };
    setSignalData(synthetic);
    setIsScanner(true);
    setTradeId(id);
    await postHistoryAdd(id, synthetic, expiry, true, dogonStep);
    setFlowStep("confirmed");
    setActiveTab("signal");
  }

  // ── derived values ────────────────────────────────────────────────────────
  const sigColor     = (s) => s === "UP" ? C.green : s === "DOWN" ? C.red : C.muted;
  const isOtc        = OTC_ASSETS.has(symbol);
  const tvSymbol     = ASSET_TV[symbol] ?? null;   // null for Deriv synthetics
  const categoryList = CATEGORIES[category] || [];
  const inFlow       = flowStep !== "idle";
  const activeIsReal = signalData?.signal === "UP" || signalData?.signal === "DOWN";
  const activeTFMins = TF_MINS[signalData?.timeframe || timeframe] || 1;

  // ── render helpers ────────────────────────────────────────────────────────

  function DogonBadge({ step }) {
    if (!step) return null;
    return (
      <div style={{ background: "rgba(249,115,22,0.15)", border: "1px solid rgba(249,115,22,0.3)", borderRadius: "8px", padding: "5px 12px", marginBottom: "12px", color: C.orange, fontWeight: 700, fontSize: "13px", textAlign: "center" }}>
        ДОГОН {step}/3
      </div>
    );
  }

  function ScannerBadge({ tf }) {
    return (
      <div style={{ background: "rgba(167,139,250,0.15)", border: "1px solid rgba(167,139,250,0.3)", borderRadius: "8px", padding: "5px 12px", marginBottom: "12px", color: C.purple, fontWeight: 700, fontSize: "12px", textAlign: "center" }}>
        AI СКАНЕР · {tf}
      </div>
    );
  }

  function OtcBadge() {
    return (
      <div style={{ background: "rgba(245,158,11,0.15)", border: "1px solid rgba(245,158,11,0.3)", borderRadius: "8px", padding: "5px 12px", marginBottom: "12px", color: "#f59e0b", fontWeight: 700, fontSize: "12px", textAlign: "center" }}>
        OTC · Синтетические / прокси котировки
      </div>
    );
  }

  function ReasonsBox({ reasons }) {
    if (!reasons?.length) return null;
    return (
      <div style={{ background: C.input, borderRadius: "10px", padding: "10px 12px", border: `1px solid ${C.border}`, marginTop: "12px" }}>
        {reasons.slice(0, 3).map((r, i) => (
          <div key={i} style={{ color: "#c8d0e0", fontSize: "12px", lineHeight: "1.6" }}>• {r}</div>
        ))}
      </div>
    );
  }

  function PriceRow({ label, value, color }) {
    if (value == null) return null;
    return (
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "8px" }}>
        <span style={{ color: C.muted, fontSize: "13px" }}>{label}</span>
        <span style={{ color: color || C.text, fontSize: "13px", fontWeight: 700 }}>
          {Number(value).toLocaleString("ru-RU", { maximumFractionDigits: 5 })}
        </span>
      </div>
    );
  }

  // ── render ────────────────────────────────────────────────────────────────
  return (
    <div style={{ minHeight: "100vh", background: C.bg, display: "flex", justifyContent: "center" }}>
      <div style={{ width: "100%", maxWidth: "480px", display: "flex", flexDirection: "column", gap: "10px", padding: "16px 14px 60px" }}>

        {/* ── Header ── */}
        <div style={{ background: "linear-gradient(135deg, #0f1928 0%, #111e35 100%)", border: "1px solid rgba(59,130,246,0.2)", borderRadius: "20px", padding: "18px 20px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div>
            <div style={{ fontSize: "22px", fontWeight: 800, color: "#fff", letterSpacing: "-0.5px" }}>{symbol}</div>
            <div style={{ color: C.muted, fontSize: "12px", marginTop: "3px" }}>
              {category} · {timeframe}
              {dogonStep > 0 && !sessionStopped && (
                <span style={{ color: C.orange, marginLeft: "8px", fontWeight: 700 }}>ДОГОН {dogonStep}/3</span>
              )}
            </div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            {newsIndicator === "red"    && <span title="Важная новость в ближайший час!" style={{ fontSize: "16px", cursor: "pointer" }} onClick={() => setActiveTab("news")}>🔴</span>}
            {newsIndicator === "yellow" && <span title="Новость средней важности" style={{ fontSize: "16px", cursor: "pointer" }} onClick={() => setActiveTab("news")}>🟡</span>}
            {newsIndicator === "green"  && <span title="Новостей нет — хорошее время" style={{ fontSize: "16px", cursor: "pointer" }} onClick={() => setActiveTab("news")}>✅</span>}
            <div style={{ background: "rgba(59,130,246,0.12)", color: "#7fb0ff", padding: "7px 14px", borderRadius: "999px", fontWeight: 700, fontSize: "12px", border: "1px solid rgba(59,130,246,0.25)" }}>
              {loading ? "Анализ..." : inFlow ? "В сделке" : "Готов"}
            </div>
          </div>
        </div>

        {/* ── Tabs ── */}
        <div style={{ display: "flex", gap: "6px" }}>
          {[["signal", "Сигнал"], ["scanner", "AI Сканер"], ["session", "📈 Сессия"], ["history", "История"], ["news", "📰"]].map(([tab, label]) => (
            <button key={tab} onClick={() => setActiveTab(tab)} style={{
              flex: 1, padding: "10px 4px", borderRadius: "12px", border: "none",
              background: activeTab === tab ? C.primary : C.card,
              color: "#fff", fontWeight: 700, cursor: "pointer", fontSize: "12px",
              transition: "background 0.2s",
            }}>{label}</button>
          ))}
        </div>

        {/* ── Asset selector (shared) ── */}
        <div style={{ background: C.card, borderRadius: "16px", padding: "14px", border: `1px solid ${C.border}` }}>
          <div style={{ color: C.muted, fontSize: "11px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.7px", marginBottom: "8px" }}>Актив</div>
          <div style={{ display: "flex", gap: "6px", marginBottom: "8px", flexWrap: "wrap" }}>
            {Object.keys(CATEGORIES).map((cat) => (
              <button key={cat} onClick={() => setCategory(cat)} disabled={inFlow} style={{
                padding: "5px 10px", borderRadius: "8px",
                border: category === cat ? "1px solid rgba(59,130,246,0.4)" : `1px solid ${C.border}`,
                background: category === cat ? "rgba(59,130,246,0.2)" : C.input,
                color: category === cat ? "#7fb0ff" : C.muted,
                fontWeight: 600, fontSize: "11px", cursor: inFlow ? "default" : "pointer",
                opacity: inFlow ? 0.5 : 1,
              }}>{cat}</button>
            ))}
          </div>
          <select value={symbol} onChange={(e) => setSymbol(e.target.value)} disabled={inFlow} style={{
            width: "100%", background: C.input, color: C.text,
            border: `1px solid ${C.border}`, borderRadius: "10px",
            padding: "10px 14px", outline: "none", fontSize: "14px",
            opacity: inFlow ? 0.5 : 1,
          }}>
            {categoryList.map((item) => <option key={item} value={item}>{item}</option>)}
          </select>
        </div>

        {/* ── Chart ── */}
        {tvSymbol ? (
          <TradingViewWidget symbol={tvSymbol} interval={timeframe} />
        ) : (
          <div style={{ height: "160px", borderRadius: "16px", background: C.card, border: `1px solid ${C.border}`, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: "8px" }}>
            <div style={{ fontSize: "32px" }}>📊</div>
            <div style={{ color: C.muted, fontSize: "13px", fontWeight: 600 }}>График недоступен для синтетических индексов</div>
            <div style={{ color: C.muted, fontSize: "11px" }}>Данные поступают напрямую с Deriv API</div>
          </div>
        )}

        {/* ═══════════════════════════════════════════════════════════════════
            SIGNAL TAB
        ════════════════════════════════════════════════════════════════════ */}
        {activeTab === "signal" && (
          <>
            {/* Timeframe */}
            <div style={{ background: C.card, borderRadius: "16px", padding: "14px", border: `1px solid ${C.border}` }}>
              <div style={{ color: C.muted, fontSize: "11px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.7px", marginBottom: "8px" }}>Таймфрейм</div>
              <div style={{ display: "flex", gap: "8px" }}>
                {TIMEFRAMES.map(({ label, value }) => (
                  <button key={value} onClick={() => setTimeframe(value)} disabled={inFlow} style={{
                    flex: 1, padding: "10px 0", borderRadius: "10px",
                    border: timeframe === value ? "1px solid rgba(59,130,246,0.5)" : `1px solid ${C.border}`,
                    background: timeframe === value ? "rgba(59,130,246,0.15)" : C.input,
                    color: timeframe === value ? "#7fb0ff" : C.muted,
                    fontWeight: 700, fontSize: "14px", cursor: inFlow ? "default" : "pointer",
                    opacity: inFlow ? 0.5 : 1,
                  }}>{label}</button>
                ))}
              </div>
            </div>

            {/* Mode */}
            <div style={{ background: C.card, borderRadius: "16px", padding: "6px", border: `1px solid ${C.border}`, display: "flex", gap: "4px" }}>
              {MODES.map((m) => (
                <button key={m} onClick={() => setMode(m)} disabled={inFlow} style={{
                  flex: 1, padding: "10px 8px", borderRadius: "10px", border: "none",
                  background: mode === m ? "rgba(59,130,246,0.18)" : "transparent",
                  color: mode === m ? "#7fb0ff" : C.muted,
                  fontWeight: 700, fontSize: "13px", cursor: inFlow ? "default" : "pointer",
                  opacity: inFlow ? 0.5 : 1,
                }}>{m}</button>
              ))}
            </div>

            {/* ── STOP SESSION ── */}
            {sessionStopped && (
              <div style={{ background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)", borderRadius: "16px", padding: "24px", textAlign: "center" }}>
                <div style={{ fontSize: "32px", marginBottom: "8px" }}>🛑</div>
                <div style={{ color: C.red, fontWeight: 800, fontSize: "16px", marginBottom: "6px" }}>Стоп-сессия</div>
                <div style={{ color: C.muted, fontSize: "13px", marginBottom: "16px" }}>
                  3 догона не принесли результата. Сделай перерыв и вернись позже.
                </div>
                <button onClick={resetSession} style={{ background: C.primary, color: "#fff", border: "none", borderRadius: "10px", padding: "11px 24px", fontWeight: 700, fontSize: "14px", cursor: "pointer" }}>
                  Новая сессия
                </button>
              </div>
            )}

            {/* ── WIN FLASH ── */}
            {!sessionStopped && winFlash && (
              <div style={{ background: "rgba(16,185,129,0.15)", border: "1px solid rgba(16,185,129,0.4)", borderRadius: "16px", padding: "28px", textAlign: "center" }}>
                <div style={{ fontSize: "44px" }}>🎉</div>
                <div style={{ color: C.green, fontWeight: 800, fontSize: "22px", marginTop: "8px" }}>Выигрыш!</div>
              </div>
            )}

            {/* ── IDLE: news warning ── */}
            {!sessionStopped && !winFlash && flowStep === "idle" && newsWarning && (
              <div style={{ background: "rgba(245,158,11,0.08)", border: "1px solid rgba(245,158,11,0.35)", borderRadius: "16px", padding: "20px" }}>
                <div style={{ display: "flex", alignItems: "flex-start", gap: "10px", marginBottom: "14px" }}>
                  <span style={{ fontSize: "22px" }}>⚠️</span>
                  <div>
                    <div style={{ color: "#f59e0b", fontWeight: 800, fontSize: "14px", marginBottom: "4px" }}>ВНИМАНИЕ! Важная новость</div>
                    {newsWarning.message.split("\n").map((line, i) => (
                      <div key={i} style={{ color: "#e2c97e", fontSize: "13px", lineHeight: "1.5" }}>{line}</div>
                    ))}
                  </div>
                </div>
                <div style={{ color: C.muted, fontSize: "12px", marginBottom: "14px" }}>
                  Рекомендуем подождать после выхода новости — рынок может быть волатильным.
                </div>
                <div style={{ display: "flex", gap: "8px" }}>
                  <button onClick={newsWarning.onProceed} style={{
                    flex: 1, padding: "12px", borderRadius: "10px",
                    border: "1px solid rgba(245,158,11,0.4)", background: "rgba(245,158,11,0.12)",
                    color: "#f59e0b", fontWeight: 700, fontSize: "13px", cursor: "pointer",
                  }}>Всё равно получить сигнал</button>
                  <button onClick={() => setNewsWarning(null)} style={{
                    flex: 1, padding: "12px", borderRadius: "10px",
                    border: `1px solid ${C.border}`, background: C.card,
                    color: C.muted, fontWeight: 700, fontSize: "13px", cursor: "pointer",
                  }}>Подождать</button>
                </div>
              </div>
            )}

            {/* ── IDLE: get signal button ── */}
            {!sessionStopped && !winFlash && flowStep === "idle" && !newsWarning && (
              <button onClick={() => fetchSignal(false)} disabled={loading} style={{
                width: "100%", border: "none",
                background: loading ? "rgba(59,130,246,0.4)" : "linear-gradient(135deg, #3b82f6 0%, #6366f1 100%)",
                color: "#fff", padding: "17px", borderRadius: "16px",
                fontSize: "15px", fontWeight: 800, cursor: loading ? "not-allowed" : "pointer",
                boxShadow: loading ? "none" : "0 8px 32px rgba(59,130,246,0.3)",
                opacity: loading ? 0.7 : 1, letterSpacing: "0.5px",
              }}>
                {loading ? "АНАЛИЗИРУЮ..." : dogonStep > 0 ? `ДОГОН ${dogonStep}/3 — НОВЫЙ СИГНАЛ` : "ПОЛУЧИТЬ СИГНАЛ"}
              </button>
            )}

            {/* ── STEP 1: Signal received — confirm or skip ── */}
            {!sessionStopped && !winFlash && flowStep === "signal" && signalData && (
              <div>
                <div style={{
                  background: activeIsReal
                    ? (signalData.signal === "UP" ? "rgba(16,185,129,0.08)" : "rgba(239,68,68,0.08)")
                    : C.card,
                  border: `1px solid ${activeIsReal ? sigColor(signalData.signal) + "40" : C.border}`,
                  borderRadius: "16px", padding: "20px", marginBottom: "10px",
                }}>
                  {dogonStep > 0 && <DogonBadge step={dogonStep} />}
                  {isScanner && activeIsReal && <ScannerBadge tf={signalData.timeframe || timeframe} />}
                  {isOtc && activeIsReal && <OtcBadge />}

                  {activeIsReal ? (
                    <>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
                        <div>
                          <div style={{ color: C.muted, fontSize: "11px", fontWeight: 600, textTransform: "uppercase" }}>Направление</div>
                          <div style={{ color: sigColor(signalData.signal), fontSize: "30px", fontWeight: 900, marginTop: "2px" }}>
                            {signalData.signal === "UP" ? "ВВЕРХ ↑" : "ВНИЗ ↓"}
                          </div>
                        </div>
                        <div style={{ textAlign: "right" }}>
                          <div style={{ color: C.muted, fontSize: "11px", fontWeight: 600, textTransform: "uppercase" }}>Точность</div>
                          <div style={{ color: sigColor(signalData.signal), fontSize: "30px", fontWeight: 900, marginTop: "2px" }}>
                            {signalData.confidence}%
                          </div>
                        </div>
                      </div>
                      <div style={{ width: "100%", height: "5px", borderRadius: "999px", background: "rgba(255,255,255,0.06)", marginBottom: "14px", overflow: "hidden" }}>
                        <div style={{ height: "100%", width: signalData.confidence + "%", borderRadius: "999px", background: signalData.signal === "UP" ? `linear-gradient(90deg, ${C.primary}, ${C.green})` : `linear-gradient(90deg, ${C.orange}, ${C.red})` }} />
                      </div>
                      <PriceRow label="📍 Точка входа" value={signalData.entry_price} />
                      <ReasonsBox reasons={signalData.reasons} />
                      {/* Detailed analysis — loads in background */}
                      {activeIsReal && (detailsLoading || detailsData) && (
                        <div style={{ marginTop: "12px" }}>
                          {detailsLoading && !detailsData && (
                            <div style={{ color: C.muted, fontSize: "12px", textAlign: "center", padding: "10px", display: "flex", alignItems: "center", justifyContent: "center", gap: "6px" }}>
                              <span style={{ animation: "spin 1s linear infinite", display: "inline-block" }}>🔍</span>
                              Загружаю детальный анализ...
                            </div>
                          )}
                          {detailsData && !detailsData.error && (
                            <DetailsPanel data={detailsData} signalData={signalData} />
                          )}
                        </div>
                      )}
                    </>
                  ) : (
                    <>
                      <div style={{ color: C.text, fontWeight: 700, marginBottom: "6px" }}>Результат анализа</div>
                      <div style={{ color: C.muted, fontSize: "13px" }}>{signalData.reasons?.[0] || signalData.signal}</div>
                    </>
                  )}
                </div>

                {/* Confirm / Skip */}
                {activeIsReal ? (
                  <div style={{ display: "flex", gap: "8px" }}>
                    <button onClick={handleConfirmEntry} style={{
                      flex: 2, padding: "15px", borderRadius: "12px",
                      border: "1px solid rgba(16,185,129,0.4)", background: "rgba(16,185,129,0.15)",
                      color: C.green, fontWeight: 800, fontSize: "14px", cursor: "pointer",
                    }}>✅ Я ЗАШЁЛ</button>
                    <button onClick={handleSkip} style={{
                      flex: 1, padding: "15px", borderRadius: "12px",
                      border: `1px solid ${C.border}`, background: C.card,
                      color: C.muted, fontWeight: 700, fontSize: "14px", cursor: "pointer",
                    }}>⏭ Пропустить</button>
                  </div>
                ) : (
                  <button onClick={() => { setFlowStep("idle"); setSignalData(null); }} style={{
                    width: "100%", padding: "14px", borderRadius: "12px",
                    border: `1px solid ${C.border}`, background: C.card,
                    color: C.muted, fontWeight: 700, fontSize: "14px", cursor: "pointer",
                  }}>Получить новый сигнал</button>
                )}
              </div>
            )}

            {/* ── STEP 2: Trade confirmed — timer running ── */}
            {!sessionStopped && !winFlash && (flowStep === "confirmed" || flowStep === "result_shown") && signalData && (
              <div style={{
                background: signalData.signal === "UP" ? "rgba(16,185,129,0.08)" : "rgba(239,68,68,0.08)",
                border: `1px solid ${sigColor(signalData.signal)}40`,
                borderRadius: "16px", padding: "20px",
              }}>
                {dogonStep > 0 && <DogonBadge step={dogonStep} />}
                {isScanner && <ScannerBadge tf={signalData.timeframe || timeframe} />}
                {isOtc && <OtcBadge />}

                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
                  <div>
                    <div style={{ color: C.muted, fontSize: "11px" }}>Направление</div>
                    <div style={{ color: sigColor(signalData.signal), fontSize: "26px", fontWeight: 900 }}>
                      {signalData.signal === "UP" ? "ВВЕРХ ↑" : "ВНИЗ ↓"}
                    </div>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ color: C.muted, fontSize: "11px" }}>Точность</div>
                    <div style={{ color: sigColor(signalData.signal), fontSize: "26px", fontWeight: 900 }}>
                      {signalData.confidence}%
                    </div>
                  </div>
                </div>

                <PriceRow label="📍 Точка входа" value={signalData.entry_price} />
                <PriceRow label="⚡ Текущая цена" value={currentPrice} color={C.primary} />

                {flowStep === "confirmed" && signalData.expiry_time && (
                  <CountdownBar
                    expiryTime={signalData.expiry_time}
                    totalMins={activeTFMins}
                    onExpire={handleTimerExpire}
                  />
                )}

                {/* ── STEP 3: Timer expired — ask result ── */}
                {flowStep === "result_shown" && (
                  <div style={{ marginTop: "16px" }}>
                    <div style={{ color: C.text, fontWeight: 700, fontSize: "15px", textAlign: "center", marginBottom: "12px" }}>
                      Сделка закрылась?
                    </div>
                    <div style={{ display: "flex", gap: "8px" }}>
                      <button onClick={handleWin} style={{
                        flex: 1, padding: "15px", borderRadius: "12px",
                        border: "1px solid rgba(16,185,129,0.4)", background: "rgba(16,185,129,0.15)",
                        color: C.green, fontWeight: 800, fontSize: "15px", cursor: "pointer",
                      }}>✅ В ПЛЮСЕ</button>
                      <button onClick={handleLoss} style={{
                        flex: 1, padding: "15px", borderRadius: "12px",
                        border: "1px solid rgba(239,68,68,0.4)", background: "rgba(239,68,68,0.15)",
                        color: C.red, fontWeight: 800, fontSize: "15px", cursor: "pointer",
                      }}>❌ В МИНУСЕ</button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </>
        )}

        {/* ═══════════════════════════════════════════════════════════════════
            SCANNER TAB
        ════════════════════════════════════════════════════════════════════ */}
        {activeTab === "scanner" && (
          <>
            {/* Timeframe + mode */}
            <div style={{ background: C.card, borderRadius: "16px", padding: "14px", border: `1px solid ${C.border}` }}>
              <div style={{ color: C.muted, fontSize: "11px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.7px", marginBottom: "8px" }}>Таймфрейм</div>
              <div style={{ display: "flex", gap: "8px" }}>
                {TIMEFRAMES.map(({ label, value }) => (
                  <button key={value} onClick={() => setTimeframe(value)} style={{
                    flex: 1, padding: "9px 0", borderRadius: "10px",
                    border: timeframe === value ? "1px solid rgba(59,130,246,0.5)" : `1px solid ${C.border}`,
                    background: timeframe === value ? "rgba(59,130,246,0.15)" : C.input,
                    color: timeframe === value ? "#7fb0ff" : C.muted,
                    fontWeight: 700, fontSize: "13px", cursor: "pointer",
                  }}>{label}</button>
                ))}
              </div>
            </div>
            <div style={{ background: C.card, borderRadius: "16px", padding: "6px", border: `1px solid ${C.border}`, display: "flex", gap: "4px" }}>
              {MODES.map((m) => (
                <button key={m} onClick={() => setMode(m)} style={{
                  flex: 1, padding: "10px 8px", borderRadius: "10px", border: "none",
                  background: mode === m ? "rgba(59,130,246,0.18)" : "transparent",
                  color: mode === m ? "#7fb0ff" : C.muted,
                  fontWeight: 700, fontSize: "13px", cursor: "pointer",
                }}>{m}</button>
              ))}
            </div>

            <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: "16px", padding: "14px 18px", textAlign: "center", color: C.green, fontWeight: 600, fontSize: "13px" }}>
              AI сканер проверит все таймфреймы и выберет лучший вход
            </div>

            <button onClick={fetchScan} disabled={scanLoading} style={{
              width: "100%", border: "none",
              background: scanLoading ? "rgba(59,130,246,0.4)" : "linear-gradient(135deg, #3b82f6 0%, #6366f1 100%)",
              color: "#fff", padding: "17px", borderRadius: "16px",
              fontSize: "15px", fontWeight: 800, cursor: scanLoading ? "not-allowed" : "pointer",
              opacity: scanLoading ? 0.7 : 1, letterSpacing: "0.5px",
            }}>
              {scanLoading ? "СКАНИРУЮ ТАЙМФРЕЙМЫ..." : "ЗАПУСТИТЬ AI СКАНЕР"}
            </button>

            {scanData && (
              <>
                {/* Best signal */}
                {scanData.best ? (
                  <div style={{
                    background: scanData.best.signal === "UP" ? "rgba(16,185,129,0.08)" : "rgba(239,68,68,0.08)",
                    border: `1px solid ${sigColor(scanData.best.signal)}40`,
                    borderRadius: "16px", padding: "18px",
                  }}>
                    <div style={{ color: C.muted, fontSize: "11px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.6px", marginBottom: "8px" }}>Лучший вход</div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "12px" }}>
                      <div>
                        <span style={{ fontSize: "24px", fontWeight: 900, color: sigColor(scanData.best.signal) }}>
                          {scanData.best.signal === "UP" ? "ВВЕРХ ↑" : "ВНИЗ ↓"}
                        </span>
                        <span style={{ fontSize: "15px", marginLeft: "10px", fontWeight: 600, color: C.muted }}>
                          {scanData.best.timeframe}
                        </span>
                      </div>
                      <span style={{ fontSize: "24px", fontWeight: 900, color: sigColor(scanData.best.signal) }}>
                        {scanData.best.confidence}%
                      </span>
                    </div>
                    <PriceRow label="📍 Точка входа" value={scanData.best.entry_price} />
                    <div style={{ color: C.muted, fontSize: "12px", marginBottom: "14px", lineHeight: "1.5" }}>
                      {scanData.reason}
                    </div>
                    <div style={{ display: "flex", gap: "8px" }}>
                      <button onClick={() => handleScannerConfirm(scanData.best)} style={{
                        flex: 2, padding: "13px", borderRadius: "12px",
                        border: "1px solid rgba(16,185,129,0.4)", background: "rgba(16,185,129,0.15)",
                        color: C.green, fontWeight: 800, fontSize: "14px", cursor: "pointer",
                      }}>✅ Я ЗАШЁЛ</button>
                      <button onClick={() => setScanData(null)} style={{
                        flex: 1, padding: "13px", borderRadius: "12px",
                        border: `1px solid ${C.border}`, background: C.card,
                        color: C.muted, fontWeight: 700, fontSize: "14px", cursor: "pointer",
                      }}>⏭ Пропустить</button>
                    </div>
                  </div>
                ) : (
                  <div style={{ background: "rgba(100,116,139,0.1)", borderRadius: "12px", padding: "16px", textAlign: "center", color: C.muted, fontSize: "13px" }}>
                    {scanData.reason}
                  </div>
                )}

                {/* All timeframes */}
                <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: "16px", padding: "16px" }}>
                  <div style={{ color: C.muted, fontSize: "11px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.7px", marginBottom: "10px" }}>Все таймфреймы</div>
                  {scanData.results.map((item, idx) => (
                    <div key={idx} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 0", borderBottom: idx < scanData.results.length - 1 ? `1px solid ${C.border}` : "none" }}>
                      <span style={{ fontWeight: 700, fontSize: "14px", color: scanData.best?.timeframe === item.timeframe ? sigColor(item.signal) : C.text }}>
                        {item.timeframe}{scanData.best?.timeframe === item.timeframe && " ★"}
                      </span>
                      <div style={{ display: "flex", gap: "12px" }}>
                        <span style={{ fontSize: "13px", fontWeight: 700, color: sigColor(item.signal) }}>
                          {item.signal === "UP" ? "ВВЕРХ" : item.signal === "DOWN" ? "ВНИЗ" : item.signal}
                        </span>
                        <span style={{ fontSize: "13px", fontWeight: 700, color: item.confidence > 0 ? sigColor(item.signal) : C.muted }}>
                          {item.confidence > 0 ? item.confidence + "%" : "--"}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            )}
          </>
        )}

        {/* ═══════════════════════════════════════════════════════════════════
            SESSION TAB
        ════════════════════════════════════════════════════════════════════ */}
        {activeTab === "session" && (
          <>
            {!sessionData ? (
              /* Start session screen */
              <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: "16px", padding: "20px" }}>
                <div style={{ color: C.text, fontWeight: 800, fontSize: "16px", marginBottom: "16px", textAlign: "center" }}>📈 Торговая сессия</div>
                <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
                  <div>
                    <div style={{ color: C.muted, fontSize: "11px", fontWeight: 600, textTransform: "uppercase", marginBottom: "5px" }}>Депозит ($)</div>
                    <input type="number" value={sessionDeposit} onChange={e => setSessionDeposit(e.target.value)}
                      style={{ width: "100%", background: C.input, color: C.text, border: `1px solid ${C.border}`, borderRadius: "10px", padding: "10px 14px", outline: "none", fontSize: "15px", boxSizing: "border-box" }} />
                  </div>
                  <div>
                    <div style={{ color: C.muted, fontSize: "11px", fontWeight: 600, textTransform: "uppercase", marginBottom: "5px" }}>Риск на сделку (%)</div>
                    <input type="number" value={sessionRisk} onChange={e => setSessionRisk(e.target.value)}
                      style={{ width: "100%", background: C.input, color: C.text, border: `1px solid ${C.border}`, borderRadius: "10px", padding: "10px 14px", outline: "none", fontSize: "15px", boxSizing: "border-box" }} />
                  </div>
                  <div>
                    <div style={{ color: C.muted, fontSize: "11px", fontWeight: 600, textTransform: "uppercase", marginBottom: "5px" }}>Макс. догонов</div>
                    <div style={{ display: "flex", gap: "6px" }}>
                      {[1,2,3].map(n => (
                        <button key={n} onClick={() => setSessionMaxMart(n)} style={{
                          flex:1, padding:"10px", borderRadius:"10px", fontWeight:700, fontSize:"14px", cursor:"pointer",
                          border: sessionMaxMart===n ? "1px solid rgba(59,130,246,0.5)" : `1px solid ${C.border}`,
                          background: sessionMaxMart===n ? "rgba(59,130,246,0.15)" : C.input,
                          color: sessionMaxMart===n ? "#7fb0ff" : C.muted,
                        }}>{n}</button>
                      ))}
                    </div>
                  </div>
                  {/* Trade size preview */}
                  {sessionDeposit && sessionRisk && (
                    <div style={{ background: C.input, borderRadius: "10px", padding: "10px 12px", border: `1px solid ${C.border}` }}>
                      <div style={{ color: C.muted, fontSize: "11px", fontWeight: 600, textTransform: "uppercase", marginBottom: "6px" }}>Размер сделок</div>
                      {[0,1,2,3].slice(0, sessionMaxMart+1).map(step => {
                        const base = parseFloat(sessionDeposit) * parseFloat(sessionRisk) / 100;
                        const size = base * Math.pow(2, step);
                        return (
                          <div key={step} style={{ display: "flex", justifyContent: "space-between", fontSize: "12px", color: step===0 ? C.text : C.orange, marginBottom: "2px" }}>
                            <span>{step === 0 ? "Базовая" : `Догон ${step}`}</span>
                            <strong>${size.toFixed(2)}</strong>
                          </div>
                        );
                      })}
                    </div>
                  )}
                  <button onClick={startSession} disabled={sessionLoading} style={{
                    width: "100%", padding: "16px", borderRadius: "12px", border: "none",
                    background: "linear-gradient(135deg, #10b981, #059669)",
                    color: "#fff", fontWeight: 800, fontSize: "15px", cursor: "pointer",
                    opacity: sessionLoading ? 0.7 : 1,
                  }}>🚀 {sessionLoading ? "Запускаю..." : "НАЧАТЬ СЕССИЮ"}</button>
                </div>
              </div>
            ) : (
              /* Active session screen */
              <>
                <div style={{ background: "rgba(16,185,129,0.08)", border: "1px solid rgba(16,185,129,0.3)", borderRadius: "16px", padding: "18px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "14px" }}>
                    <div style={{ color: C.green, fontWeight: 800, fontSize: "14px" }}>🟢 СЕССИЯ АКТИВНА</div>
                    <div style={{ color: C.muted, fontSize: "12px" }}>
                      {sessionData.started_at ? new Date(sessionData.started_at).toLocaleTimeString("ru-RU",{hour:"2-digit",minute:"2-digit"}) : ""}
                    </div>
                  </div>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", marginBottom: "14px" }}>
                    <div style={{ background: C.input, borderRadius: "10px", padding: "10px", textAlign: "center" }}>
                      <div style={{ color: C.green, fontSize: "20px", fontWeight: 800 }}>{sessionData.wins || 0}</div>
                      <div style={{ color: C.muted, fontSize: "11px" }}>✅ Выиграно</div>
                    </div>
                    <div style={{ background: C.input, borderRadius: "10px", padding: "10px", textAlign: "center" }}>
                      <div style={{ color: C.red, fontSize: "20px", fontWeight: 800 }}>{sessionData.losses || 0}</div>
                      <div style={{ color: C.muted, fontSize: "11px" }}>❌ Проиграно</div>
                    </div>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "10px" }}>
                    <span style={{ color: C.muted, fontSize: "13px" }}>Win Rate</span>
                    <strong style={{ color: C.green, fontSize: "13px" }}>
                      {(sessionData.wins||0)+(sessionData.losses||0) > 0
                        ? Math.round((sessionData.wins||0)/((sessionData.wins||0)+(sessionData.losses||0))*100) + "%"
                        : "—"}
                    </strong>
                  </div>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "14px" }}>
                    <span style={{ color: C.muted, fontSize: "13px" }}>P&L</span>
                    <strong style={{ color: (sessionData.pnl||0) >= 0 ? C.green : C.red, fontSize: "13px" }}>
                      {(sessionData.pnl||0) >= 0 ? "+" : ""}${(sessionData.pnl||0).toFixed(2)}
                    </strong>
                  </div>
                  {/* Next trade size */}
                  {sessionData.deposit && sessionData.risk_pct && (
                    <div style={{ background: C.input, borderRadius: "10px", padding: "10px 12px", marginBottom: "14px" }}>
                      <div style={{ color: C.muted, fontSize: "11px", fontWeight: 600, textTransform: "uppercase", marginBottom: "4px" }}>Следующая сделка</div>
                      {(() => {
                        const base = sessionData.deposit * sessionData.risk_pct / 100;
                        const step = dogonStep;
                        const size = base * Math.pow(2, step);
                        return (
                          <div style={{ display: "flex", justifyContent: "space-between" }}>
                            <span style={{ color: C.muted, fontSize: "12px" }}>{step === 0 ? "Базовая" : `Догон ${step}`}</span>
                            <strong style={{ color: step === 0 ? C.text : C.orange, fontSize: "14px" }}>${size.toFixed(2)}</strong>
                          </div>
                        );
                      })()}
                    </div>
                  )}
                  <div style={{ display: "flex", gap: "8px" }}>
                    <button onClick={fetchCurrentSession} style={{
                      flex:1, padding:"12px", borderRadius:"10px",
                      border:`1px solid ${C.border}`, background:C.card,
                      color:C.muted, fontWeight:600, fontSize:"13px", cursor:"pointer",
                    }}>🔄 Обновить</button>
                    <button onClick={endSession} disabled={sessionLoading} style={{
                      flex:1, padding:"12px", borderRadius:"10px",
                      border:"1px solid rgba(239,68,68,0.4)", background:"rgba(239,68,68,0.1)",
                      color:C.red, fontWeight:700, fontSize:"13px", cursor:"pointer",
                      opacity: sessionLoading ? 0.7 : 1,
                    }}>🛑 Завершить</button>
                  </div>
                </div>
              </>
            )}
          </>
        )}

        {/* ═══════════════════════════════════════════════════════════════════
            HISTORY TAB
        ════════════════════════════════════════════════════════════════════ */}
        {activeTab === "history" && (
          <>
            {/* Stats */}
            {historyData?.stats && (
              <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: "16px", padding: "18px" }}>
                <div style={{ color: C.muted, fontSize: "11px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.7px", marginBottom: "12px" }}>Статистика Win Rate</div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "12px", textAlign: "center", marginBottom: "14px" }}>
                  <div><div style={{ color: C.green, fontSize: "22px", fontWeight: 800 }}>{historyData.stats.win_rate}%</div><div style={{ color: C.muted, fontSize: "11px", marginTop: "2px" }}>Общий</div></div>
                  <div><div style={{ color: C.primary, fontSize: "22px", fontWeight: 800 }}>{historyData.stats.win_rate_manual}%</div><div style={{ color: C.muted, fontSize: "11px", marginTop: "2px" }}>Ручной</div></div>
                  <div><div style={{ color: C.purple, fontSize: "22px", fontWeight: 800 }}>{historyData.stats.win_rate_ai}%</div><div style={{ color: C.muted, fontSize: "11px", marginTop: "2px" }}>AI Сканер</div></div>
                </div>
                <div style={{ display: "flex", justifyContent: "space-around", paddingTop: "12px", borderTop: `1px solid ${C.border}` }}>
                  <span style={{ color: C.muted, fontSize: "12px" }}>Всего: <strong style={{ color: C.text }}>{historyData.stats.total}</strong></span>
                  <span style={{ color: C.green, fontSize: "12px" }}>✅ {historyData.stats.wins}</span>
                  <span style={{ color: C.red,   fontSize: "12px" }}>❌ {historyData.stats.losses}</span>
                  {historyData.stats.streak > 0 && (
                    <span style={{ color: historyData.stats.streak_type === "WIN" ? C.green : C.red, fontSize: "12px" }}>
                      {historyData.stats.streak_type === "WIN" ? "🔥" : "📉"}×{historyData.stats.streak}
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* Filters */}
            <div style={{ display: "flex", gap: "6px" }}>
              {[["all","Все"], ["manual","Ручной"], ["ai_scanner","AI Сканер"]].map(([v,l]) => (
                <button key={v} onClick={() => { setHistoryModeFilter(v); fetchHistory(true); }} style={{
                  flex:1, padding:"8px 4px", borderRadius:"10px", border:"none", fontWeight:700, fontSize:"12px", cursor:"pointer",
                  background: historyModeFilter===v ? C.primary : C.card, color:"#fff",
                }}>{l}</button>
              ))}
            </div>
            <div style={{ display: "flex", gap: "6px" }}>
              {[["all","Все"], ["WIN","Выиграл"], ["LOSS","Проиграл"]].map(([v,l]) => (
                <button key={v} onClick={() => { setHistoryResultFilter(v); fetchHistory(true); }} style={{
                  flex:1, padding:"8px 4px", borderRadius:"10px", border:"none", fontWeight:700, fontSize:"12px", cursor:"pointer",
                  background: historyResultFilter===v ? (v==="WIN"?C.green:v==="LOSS"?C.red:C.primary) : C.card, color:"#fff",
                }}>{l}</button>
              ))}
            </div>

            {/* Trade list */}
            {historyData?.history?.length > 0 ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
                {historyData.history.map((trade, idx) => (
                  <TradeCard key={trade.trade_id || idx} trade={trade} />
                ))}
              </div>
            ) : (
              <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: "16px", padding: "32px", textAlign: "center", color: C.muted, fontSize: "14px" }}>
                История пуста. Заходи в сделки — они появятся здесь.
              </div>
            )}

            {historyHasMore && (
              <button onClick={() => fetchHistory(false)} style={{
                width:"100%", padding:"12px", borderRadius:"12px",
                border:`1px solid ${C.border}`, background:C.card,
                color:C.muted, fontWeight:600, fontSize:"13px", cursor:"pointer",
              }}>Загрузить ещё</button>
            )}

            <button onClick={() => fetchHistory(true)} style={{
              width:"100%", padding:"12px", borderRadius:"12px",
              border:`1px solid ${C.border}`, background:C.card,
              color:C.muted, fontWeight:600, fontSize:"13px", cursor:"pointer",
            }}>Обновить</button>
          </>
        )}

        {/* ═══════════════════════════════════════════════════════════════════
            NEWS TAB
        ════════════════════════════════════════════════════════════════════ */}
        {activeTab === "news" && (
          <>
            {/* Currency filter */}
            <div style={{ background: C.card, borderRadius: "16px", padding: "12px 14px", border: `1px solid ${C.border}` }}>
              <div style={{ color: C.muted, fontSize: "11px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.7px", marginBottom: "8px" }}>Валюта</div>
              <div style={{ display: "flex", gap: "5px", flexWrap: "wrap" }}>
                {["ALL","USD","EUR","GBP","JPY","AUD","CAD","CHF","NZD"].map(c => (
                  <button key={c} onClick={() => setNewsCurrencyFilter(c)} style={{
                    padding: "5px 10px", borderRadius: "8px", fontWeight: 700, fontSize: "12px", cursor: "pointer",
                    border: newsCurrencyFilter === c ? "1px solid rgba(59,130,246,0.5)" : `1px solid ${C.border}`,
                    background: newsCurrencyFilter === c ? "rgba(59,130,246,0.18)" : C.input,
                    color: newsCurrencyFilter === c ? "#7fb0ff" : C.muted,
                  }}>{c}</button>
                ))}
              </div>
            </div>

            {/* Impact filter */}
            <div style={{ background: C.card, borderRadius: "16px", padding: "6px", border: `1px solid ${C.border}`, display: "flex", gap: "4px" }}>
              {[["all","Все события"], ["important","Только важные"]].map(([v, l]) => (
                <button key={v} onClick={() => setNewsImpactFilter(v)} style={{
                  flex: 1, padding: "9px 8px", borderRadius: "10px", border: "none",
                  background: newsImpactFilter === v ? "rgba(59,130,246,0.18)" : "transparent",
                  color: newsImpactFilter === v ? "#7fb0ff" : C.muted,
                  fontWeight: 700, fontSize: "13px", cursor: "pointer",
                }}>{l}</button>
              ))}
            </div>

            {/* Event list */}
            {newsLoading ? (
              <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: "16px", padding: "32px", textAlign: "center", color: C.muted, fontSize: "14px" }}>
                Загрузка новостей...
              </div>
            ) : newsData?.events?.length > 0 ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "6px" }}>
                {(() => {
                  const filtered = newsData.events.filter(e => newsImpactFilter === "all" || e.impact !== "low");
                  if (filtered.length === 0) return (
                    <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: "16px", padding: "32px", textAlign: "center", color: C.muted, fontSize: "14px" }}>
                      Важных новостей нет
                    </div>
                  );
                  return filtered.map((ev, i) => <NewsEventCard key={i} event={ev} />);
                })()}
              </div>
            ) : (
              <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: "16px", padding: "32px", textAlign: "center" }}>
                <div style={{ fontSize: "32px", marginBottom: "8px" }}>📅</div>
                <div style={{ color: C.muted, fontSize: "14px" }}>Нет данных. Нажмите обновить.</div>
              </div>
            )}

            <button onClick={fetchNewsTab} disabled={newsLoading} style={{
              width: "100%", padding: "12px", borderRadius: "12px",
              border: `1px solid ${C.border}`, background: C.card,
              color: C.muted, fontWeight: 600, fontSize: "13px", cursor: "pointer",
              opacity: newsLoading ? 0.5 : 1,
            }}>
              {newsLoading ? "Обновляется..." : "Обновить"}
            </button>
          </>
        )}

      </div>
    </div>
  );
}
