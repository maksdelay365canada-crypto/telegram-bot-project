import "./App.css";
import { useState, useEffect } from "react";

const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const ASSET_TV = {
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
};

const CATEGORIES = {
  "Форекс": ["EUR/USD","GBP/USD","AUD/USD","USD/JPY","USD/CAD","USD/CHF","EUR/GBP","EUR/JPY","EUR/CHF","EUR/AUD","EUR/CAD","GBP/JPY","GBP/CHF","GBP/AUD","GBP/CAD","AUD/JPY","AUD/CAD","AUD/CHF","CAD/JPY","CAD/CHF","CHF/JPY","NZD/USD","NZD/JPY","NZD/CAD","NZD/CHF","NZD/GBP"],
  "Крипто": ["Bitcoin","Ethereum","Dash","Chainlink","Bitcoin Cash"],
  "Акции": ["Apple","Microsoft","Tesla","Netflix","Amazon","Google","Meta","Intel","Cisco","ExxonMobil","Johnson & Johnson","Pfizer","Boeing","McDonald's","JPMorgan","American Express","Citigroup","Alibaba"],
  "Индексы": ["US100","SP500","DJI30","DAX","FTSE 100","CAC 40","Nikkei 225","AUS 200","Euro Stoxx 50","Hang Seng"],
  "Товары": ["Gold","Silver","Oil Brent","Oil WTI","Natural Gas","Platinum"],
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
  text: "#f1f5f9",
  muted: "#64748b",
  border: "rgba(255,255,255,0.07)",
};

function TradingViewWidget({ symbol, interval }) {
  const containerId = "tv-widget-container";
  useEffect(() => {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = "";
    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";
    script.async = true;
    script.innerHTML = JSON.stringify({
      autosize: true,
      symbol: symbol,
      interval: interval === "M1" ? "1" : interval === "M3" ? "3" : interval === "M5" ? "5" : "15",
      timezone: "Etc/UTC",
      theme: "dark",
      style: "1",
      locale: "ru",
      enable_publishing: false,
      hide_top_toolbar: false,
      hide_legend: true,
      save_image: false,
      container_id: containerId,
    });
    container.appendChild(script);
  }, [symbol, interval]);

  return (
    <div style={{ height: "300px", width: "100%", borderRadius: "16px", overflow: "hidden", background: C.card }}>
      <div id={containerId} style={{ height: "100%", width: "100%" }} />
    </div>
  );
}

function CountdownBar({ expiryTime, timeframeMins }) {
  const totalSecs = timeframeMins * 60;
  const [remaining, setRemaining] = useState(totalSecs);

  useEffect(() => {
    if (!expiryTime) return;
    const tick = () => {
      const diff = Math.max(0, Math.round((new Date(expiryTime) - Date.now()) / 1000));
      setRemaining(diff);
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [expiryTime]);

  const pct = totalSecs > 0 ? (remaining / totalSecs) * 100 : 0;
  const h = String(Math.floor(remaining / 3600)).padStart(2, "0");
  const m = String(Math.floor((remaining % 3600) / 60)).padStart(2, "0");
  const s = String(remaining % 60).padStart(2, "0");

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px" }}>
        <span style={{ color: C.muted, fontSize: "12px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.6px" }}>До истечения</span>
        <span style={{ color: remaining < 30 ? C.red : C.text, fontSize: "14px", fontWeight: 700, fontVariantNumeric: "tabular-nums" }}>
          {h}:{m}:{s}
        </span>
      </div>
      <div style={{ width: "100%", height: "6px", borderRadius: "999px", background: "rgba(255,255,255,0.06)", overflow: "hidden" }}>
        <div style={{
          height: "100%",
          width: pct + "%",
          borderRadius: "999px",
          background: pct > 40 ? `linear-gradient(90deg, ${C.primary}, ${C.green})` : `linear-gradient(90deg, ${C.red}, #f97316)`,
          transition: "width 1s linear",
        }} />
      </div>
    </div>
  );
}

export default function App() {
  const [category, setCategory] = useState("Форекс");
  const [symbol, setSymbol] = useState("EUR/USD");
  const [timeframe, setTimeframe] = useState("M1");
  const [mode, setMode] = useState("Уверенный");
  const [signalData, setSignalData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dogonStep, setDogonStep] = useState(0);
  const [sessionStopped, setSessionStopped] = useState(false);
  const [resultShown, setResultShown] = useState(false);
  const [winFlash, setWinFlash] = useState(false);
  const [activeTab, setActiveTab] = useState("signal");
  const [scanData, setScanData] = useState(null);
  const [scanLoading, setScanLoading] = useState(false);

  const timeframeMins = { M1: 1, M3: 3, M5: 5, M15: 15 };

  // When category changes, reset symbol to first in new category
  useEffect(() => {
    const list = CATEGORIES[category];
    if (list && !list.includes(symbol)) {
      setSymbol(list[0]);
    }
  }, [category]);

  // When expiry passes, show result buttons
  useEffect(() => {
    if (!signalData?.expiry_time) return;
    setResultShown(false);
    const diff = new Date(signalData.expiry_time) - Date.now();
    if (diff <= 0) {
      setResultShown(true);
      return;
    }
    const id = setTimeout(() => setResultShown(true), diff);
    return () => clearTimeout(id);
  }, [signalData?.expiry_time]);

  function playSound(type) {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const freqs = type === "win" ? [523, 659, 784] : [400, 300];
      freqs.forEach((freq, i) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.frequency.value = freq;
        osc.type = "sine";
        const t = ctx.currentTime + i * 0.12;
        gain.gain.setValueAtTime(0.25, t);
        gain.gain.exponentialRampToValueAtTime(0.001, t + 0.35);
        osc.start(t);
        osc.stop(t + 0.35);
      });
    } catch (_) {}
  }

  async function fetchSignal() {
    if (loading) return;
    setLoading(true);
    setResultShown(false);
    try {
      const res = await fetch(`${API}/signal`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol, timeframe, mode }),
      });
      const data = await res.json();
      setSignalData(data);
      if (data.signal === "UP" || data.signal === "DOWN") {
        playSound("signal");
      }
    } catch (_) {
      setSignalData({
        signal: "ERROR", confidence: 0,
        reasons: ["Ошибка подключения к серверу"],
        state: "neutral", symbol, timeframe, mode,
        timestamp: new Date().toISOString(),
        expiry_time: new Date(Date.now() + 60000).toISOString(),
        win_rate: 0,
      });
    } finally {
      setLoading(false);
    }
  }

  function handleWin() {
    playSound("win");
    setWinFlash(true);
    setTimeout(() => setWinFlash(false), 1800);
    setDogonStep(0);
    setSessionStopped(false);
    setSignalData(null);
    setResultShown(false);
  }

  function handleLoss() {
    if (dogonStep >= 3) {
      setSessionStopped(true);
      return;
    }
    const next = dogonStep + 1;
    setDogonStep(next);
    if (next > 3) {
      setSessionStopped(true);
    } else {
      fetchSignal(true);
    }
  }

  function resetSession() {
    setDogonStep(0);
    setSessionStopped(false);
    setSignalData(null);
    setResultShown(false);
  }

  async function fetchScan() {
    setScanLoading(true);
    setScanData(null);
    try {
      const res = await fetch(`${API}/scan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol, timeframe: "M1", mode }),
      });
      const data = await res.json();
      setScanData(data);
    } catch (_) {
      setScanData({ results: [], best: null, reason: "Ошибка подключения к серверу" });
    } finally {
      setScanLoading(false);
    }
  }

  const sigColor = (sig) => sig === "UP" ? C.green : sig === "DOWN" ? C.red : C.muted;
  const tvSymbol = ASSET_TV[symbol] || "FX:EURUSD";
  const categoryList = CATEGORIES[category] || [];
  const isActive = signalData && (signalData.signal === "UP" || signalData.signal === "DOWN");

  return (
    <div style={{
      minHeight: "100vh",
      background: C.bg,
      display: "flex",
      justifyContent: "center",
      padding: "0",
    }}>
      <div style={{
        width: "100%",
        maxWidth: "480px",
        display: "flex",
        flexDirection: "column",
        gap: "10px",
        padding: "16px 14px 60px",
      }}>

        {/* Header */}
        <div style={{
          background: "linear-gradient(135deg, #0f1928 0%, #111e35 100%)",
          border: `1px solid rgba(59,130,246,0.2)`,
          borderRadius: "20px",
          padding: "18px 20px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}>
          <div>
            <div style={{ fontSize: "22px", fontWeight: 800, color: "#fff", letterSpacing: "-0.5px" }}>
              {symbol}
            </div>
            <div style={{ color: C.muted, fontSize: "12px", marginTop: "3px" }}>
              {category} · {timeframe}
              {dogonStep > 0 && !sessionStopped && (
                <span style={{ color: "#f97316", marginLeft: "8px", fontWeight: 700 }}>
                  ДОГОН {dogonStep}/3
                </span>
              )}
            </div>
          </div>
          <div style={{
            background: "rgba(59,130,246,0.12)",
            color: "#7fb0ff",
            padding: "7px 14px",
            borderRadius: "999px",
            fontWeight: 700,
            fontSize: "12px",
            border: "1px solid rgba(59,130,246,0.25)",
          }}>
            {loading ? "Анализ..." : isActive ? "Сигнал" : "Готов"}
          </div>
        </div>

        {/* Tabs */}
        <div style={{ display: "flex", gap: "8px" }}>
          {[["signal", "Сигнал"], ["scanner", "AI Сканер"]].map(([tab, label]) => (
            <button key={tab} onClick={() => setActiveTab(tab)} style={{
              flex: 1, padding: "11px", borderRadius: "12px", border: "none",
              background: activeTab === tab ? C.primary : C.card,
              color: "#fff", fontWeight: 700, cursor: "pointer", fontSize: "13px",
              transition: "all 0.2s",
            }}>{label}</button>
          ))}
        </div>

        {/* Asset selector */}
        <div style={{ background: C.card, borderRadius: "16px", padding: "16px", border: `1px solid ${C.border}` }}>
          <div style={{ color: C.muted, fontSize: "11px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.7px", marginBottom: "10px" }}>Актив</div>
          <div style={{ display: "flex", gap: "6px", marginBottom: "10px", flexWrap: "wrap" }}>
            {Object.keys(CATEGORIES).map((cat) => (
              <button key={cat} onClick={() => setCategory(cat)} style={{
                padding: "6px 12px", borderRadius: "8px", border: "none",
                background: category === cat ? "rgba(59,130,246,0.2)" : C.input,
                color: category === cat ? "#7fb0ff" : C.muted,
                fontWeight: 600, fontSize: "12px", cursor: "pointer",
                border: category === cat ? "1px solid rgba(59,130,246,0.4)" : `1px solid ${C.border}`,
                transition: "all 0.15s",
              }}>{cat}</button>
            ))}
          </div>
          <select
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            style={{
              width: "100%", background: C.input, color: C.text,
              border: `1px solid ${C.border}`, borderRadius: "10px",
              padding: "11px 14px", outline: "none", fontSize: "14px",
              appearance: "none", WebkitAppearance: "none",
              backgroundImage: "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%2364748b' d='M6 8L1 3h10z'/%3E%3C/svg%3E\")",
              backgroundRepeat: "no-repeat",
              backgroundPosition: "right 14px center",
              paddingRight: "36px",
            }}
          >
            {categoryList.map((item) => (
              <option key={item} value={item}>{item}</option>
            ))}
          </select>
        </div>

        {/* TradingView chart */}
        <TradingViewWidget symbol={tvSymbol} interval={timeframe} />

        {/* Timeframe selector */}
        <div style={{ background: C.card, borderRadius: "16px", padding: "16px", border: `1px solid ${C.border}` }}>
          <div style={{ color: C.muted, fontSize: "11px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.7px", marginBottom: "10px" }}>Таймфрейм</div>
          <div style={{ display: "flex", gap: "8px" }}>
            {TIMEFRAMES.map(({ label, value }) => (
              <button key={value} onClick={() => setTimeframe(value)} style={{
                flex: 1, padding: "10px 0", borderRadius: "10px",
                border: timeframe === value ? "1px solid rgba(59,130,246,0.5)" : `1px solid ${C.border}`,
                background: timeframe === value ? "rgba(59,130,246,0.15)" : C.input,
                color: timeframe === value ? "#7fb0ff" : C.muted,
                fontWeight: 700, fontSize: "14px", cursor: "pointer",
                transition: "all 0.15s",
              }}>{label}</button>
            ))}
          </div>
        </div>

        {/* Mode selector */}
        <div style={{
          background: C.card, borderRadius: "16px", padding: "6px",
          border: `1px solid ${C.border}`, display: "flex", gap: "4px",
        }}>
          {MODES.map((m) => (
            <button key={m} onClick={() => setMode(m)} style={{
              flex: 1, padding: "10px 8px", borderRadius: "10px", border: "none",
              background: mode === m ? "rgba(59,130,246,0.18)" : "transparent",
              color: mode === m ? "#7fb0ff" : C.muted,
              fontWeight: 700, fontSize: "13px", cursor: "pointer",
              transition: "all 0.15s",
            }}>{m}</button>
          ))}
        </div>

        {/* === SIGNAL TAB === */}
        {activeTab === "signal" && (
          <>
            {/* Session stopped */}
            {sessionStopped ? (
              <div style={{
                background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)",
                borderRadius: "16px", padding: "20px", textAlign: "center",
              }}>
                <div style={{ fontSize: "28px", marginBottom: "8px" }}>🛑</div>
                <div style={{ color: C.red, fontWeight: 800, fontSize: "16px", marginBottom: "6px" }}>
                  Стоп-сессия
                </div>
                <div style={{ color: C.muted, fontSize: "13px", marginBottom: "16px" }}>
                  3 догона не принесли результата. Сделай перерыв и вернись позже.
                </div>
                <button onClick={resetSession} style={{
                  background: C.primary, color: "#fff", border: "none",
                  borderRadius: "10px", padding: "11px 24px",
                  fontWeight: 700, fontSize: "14px", cursor: "pointer",
                }}>
                  Новая сессия
                </button>
              </div>
            ) : (
              <>
                {/* Win flash */}
                {winFlash && (
                  <div style={{
                    background: "rgba(16,185,129,0.15)", border: "1px solid rgba(16,185,129,0.4)",
                    borderRadius: "16px", padding: "16px", textAlign: "center",
                    animation: "fadeIn 0.3s ease",
                  }}>
                    <div style={{ fontSize: "32px" }}>🎉</div>
                    <div style={{ color: C.green, fontWeight: 800, fontSize: "18px", marginTop: "6px" }}>
                      Выигрыш!
                    </div>
                  </div>
                )}

                {/* Signal block */}
                {signalData && isActive && !winFlash && (
                  <div style={{
                    background: signalData.signal === "UP"
                      ? "rgba(16,185,129,0.08)" : "rgba(239,68,68,0.08)",
                    border: `1px solid ${sigColor(signalData.signal)}40`,
                    borderRadius: "16px", padding: "20px",
                  }}>
                    {dogonStep > 0 && (
                      <div style={{
                        background: "rgba(249,115,22,0.15)", border: "1px solid rgba(249,115,22,0.3)",
                        borderRadius: "8px", padding: "6px 12px", marginBottom: "14px",
                        color: "#f97316", fontWeight: 700, fontSize: "13px", textAlign: "center",
                      }}>
                        ДОГОН {dogonStep}/3
                      </div>
                    )}
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
                      <div>
                        <div style={{ color: C.muted, fontSize: "11px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.6px" }}>
                          Направление
                        </div>
                        <div style={{ color: sigColor(signalData.signal), fontSize: "28px", fontWeight: 900, marginTop: "2px" }}>
                          {signalData.signal === "UP" ? "ВВЕРХ" : "ВНИЗ"}
                          {" "}
                          {signalData.signal === "UP" ? "↑" : "↓"}
                        </div>
                      </div>
                      <div style={{ textAlign: "right" }}>
                        <div style={{ color: C.muted, fontSize: "11px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.6px" }}>
                          Точность
                        </div>
                        <div style={{ color: sigColor(signalData.signal), fontSize: "28px", fontWeight: 900, marginTop: "2px" }}>
                          {signalData.confidence}%
                        </div>
                      </div>
                    </div>

                    {/* Confidence bar */}
                    <div style={{ marginBottom: "16px" }}>
                      <div style={{ width: "100%", height: "6px", borderRadius: "999px", background: "rgba(255,255,255,0.06)", overflow: "hidden" }}>
                        <div style={{
                          height: "100%", width: signalData.confidence + "%",
                          borderRadius: "999px",
                          background: signalData.signal === "UP"
                            ? `linear-gradient(90deg, ${C.primary}, ${C.green})`
                            : `linear-gradient(90deg, #f97316, ${C.red})`,
                          transition: "width 0.5s ease",
                        }} />
                      </div>
                    </div>

                    {/* Countdown */}
                    {signalData.expiry_time && (
                      <div style={{ marginBottom: "16px" }}>
                        <CountdownBar
                          expiryTime={signalData.expiry_time}
                          timeframeMins={timeframeMins[timeframe] || 1}
                        />
                      </div>
                    )}

                    {/* Entry price */}
                    {signalData.entry_price && (
                      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "12px" }}>
                        <span style={{ color: C.muted, fontSize: "13px" }}>Цена входа</span>
                        <span style={{ color: C.text, fontSize: "13px", fontWeight: 700 }}>
                          {Number(signalData.entry_price).toLocaleString("ru-RU", { maximumFractionDigits: 5 })}
                        </span>
                      </div>
                    )}

                    {/* Win rate */}
                    {signalData.win_rate != null && (
                      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "12px" }}>
                        <span style={{ color: C.muted, fontSize: "13px" }}>Win Rate</span>
                        <span style={{ color: C.green, fontSize: "13px", fontWeight: 700 }}>
                          {signalData.win_rate}%
                        </span>
                      </div>
                    )}

                    {/* Reasons */}
                    {signalData.reasons?.length > 0 && (
                      <div style={{
                        background: C.input, borderRadius: "10px", padding: "12px",
                        border: `1px solid ${C.border}`, marginBottom: "0",
                      }}>
                        <div style={{ color: C.muted, fontSize: "11px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.6px", marginBottom: "8px" }}>
                          Причины
                        </div>
                        {signalData.reasons.map((r, i) => (
                          <div key={i} style={{ color: "#c8d0e0", fontSize: "12px", lineHeight: "1.5", marginBottom: i < signalData.reasons.length - 1 ? "4px" : 0 }}>
                            • {r}
                          </div>
                        ))}
                      </div>
                    )}

                    {/* Win/Loss buttons */}
                    {resultShown && (
                      <div style={{ display: "flex", gap: "8px", marginTop: "16px" }}>
                        <button onClick={handleWin} style={{
                          flex: 1, padding: "14px", borderRadius: "12px", border: "none",
                          background: "rgba(16,185,129,0.15)",
                          border: "1px solid rgba(16,185,129,0.4)",
                          color: C.green, fontWeight: 800, fontSize: "15px", cursor: "pointer",
                          transition: "all 0.15s",
                        }}>
                          Выиграл
                        </button>
                        <button onClick={handleLoss} style={{
                          flex: 1, padding: "14px", borderRadius: "12px", border: "none",
                          background: "rgba(239,68,68,0.15)",
                          border: "1px solid rgba(239,68,68,0.4)",
                          color: C.red, fontWeight: 800, fontSize: "15px", cursor: "pointer",
                          transition: "all 0.15s",
                        }}>
                          Проиграл
                        </button>
                      </div>
                    )}
                  </div>
                )}

                {/* NO SIGNAL result */}
                {signalData && !isActive && !winFlash && (
                  <div style={{
                    background: C.card, border: `1px solid ${C.border}`,
                    borderRadius: "16px", padding: "18px",
                  }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "10px" }}>
                      <span style={{ color: C.text, fontWeight: 700 }}>Результат анализа</span>
                      <span style={{
                        background: "rgba(100,116,139,0.2)", color: C.muted,
                        padding: "5px 12px", borderRadius: "999px",
                        fontSize: "12px", fontWeight: 700,
                      }}>
                        {signalData.signal}
                      </span>
                    </div>
                    {signalData.reasons?.length > 0 && (
                      <div style={{ color: C.muted, fontSize: "13px" }}>
                        {signalData.reasons[0]}
                      </div>
                    )}
                  </div>
                )}

                {/* Get signal button */}
                <button
                  onClick={() => fetchSignal(false)}
                  disabled={loading}
                  style={{
                    width: "100%", border: "none",
                    background: loading
                      ? "rgba(59,130,246,0.4)"
                      : "linear-gradient(135deg, #3b82f6 0%, #6366f1 100%)",
                    color: "#fff", padding: "17px", borderRadius: "16px",
                    fontSize: "15px", fontWeight: 800, cursor: loading ? "not-allowed" : "pointer",
                    boxShadow: loading ? "none" : "0 8px 32px rgba(59,130,246,0.3)",
                    transition: "all 0.2s", letterSpacing: "0.5px",
                    opacity: loading ? 0.7 : 1,
                  }}
                >
                  {loading ? "АНАЛИЗИРУЮ..." : dogonStep > 0 ? `ДОГОН ${dogonStep}/3 — НОВЫЙ СИГНАЛ` : "ПОЛУЧИТЬ СИГНАЛ"}
                </button>
              </>
            )}
          </>
        )}

        {/* === SCANNER TAB === */}
        {activeTab === "scanner" && (
          <>
            <div style={{
              background: C.card, border: `1px solid ${C.border}`,
              borderRadius: "16px", padding: "14px 18px",
              textAlign: "center", color: C.green,
              fontWeight: 600, fontSize: "13px",
            }}>
              AI сканер проверит все таймфреймы и выберет лучший вход
            </div>

            <button
              onClick={fetchScan}
              disabled={scanLoading}
              style={{
                width: "100%", border: "none",
                background: scanLoading
                  ? "rgba(59,130,246,0.4)"
                  : "linear-gradient(135deg, #3b82f6 0%, #6366f1 100%)",
                color: "#fff", padding: "17px", borderRadius: "16px",
                fontSize: "15px", fontWeight: 800,
                cursor: scanLoading ? "not-allowed" : "pointer",
                opacity: scanLoading ? 0.7 : 1,
                transition: "all 0.2s", letterSpacing: "0.5px",
              }}
            >
              {scanLoading ? "СКАНИРУЮ ТАЙМФРЕЙМЫ..." : "ЗАПУСТИТЬ AI СКАНЕР"}
            </button>

            {scanData && (
              <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: "16px", padding: "18px" }}>
                {scanData.best ? (
                  <div style={{
                    background: scanData.best.signal === "UP"
                      ? "rgba(16,185,129,0.08)" : "rgba(239,68,68,0.08)",
                    border: `1px solid ${sigColor(scanData.best.signal)}40`,
                    borderRadius: "12px", padding: "16px", marginBottom: "16px",
                  }}>
                    <div style={{ color: C.muted, fontSize: "11px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.6px", marginBottom: "6px" }}>
                      Лучший вход
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <div>
                        <span style={{ fontSize: "24px", fontWeight: 900, color: sigColor(scanData.best.signal) }}>
                          {scanData.best.signal === "UP" ? "ВВЕРХ ↑" : "ВНИЗ ↓"}
                        </span>
                        <span style={{ fontSize: "16px", marginLeft: "10px", fontWeight: 600, color: C.muted }}>
                          {scanData.best.timeframe}
                        </span>
                      </div>
                      <span style={{ fontSize: "24px", fontWeight: 900, color: sigColor(scanData.best.signal) }}>
                        {scanData.best.confidence}%
                      </span>
                    </div>
                    <div style={{ color: C.muted, fontSize: "12px", marginTop: "8px", lineHeight: "1.5" }}>
                      {scanData.reason}
                    </div>
                  </div>
                ) : (
                  <div style={{
                    background: "rgba(100,116,139,0.1)", borderRadius: "12px",
                    padding: "16px", marginBottom: "16px",
                    textAlign: "center", color: C.muted, fontSize: "13px",
                  }}>
                    {scanData.reason}
                  </div>
                )}

                <div style={{ color: C.muted, fontSize: "11px", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.7px", marginBottom: "10px" }}>
                  Все таймфреймы
                </div>
                {scanData.results.map((item, idx) => (
                  <div key={idx} style={{
                    display: "flex", justifyContent: "space-between", alignItems: "center",
                    padding: "10px 0",
                    borderBottom: idx < scanData.results.length - 1 ? `1px solid ${C.border}` : "none",
                  }}>
                    <span style={{
                      fontWeight: 700, fontSize: "14px",
                      color: scanData.best?.timeframe === item.timeframe ? sigColor(item.signal) : C.text,
                    }}>
                      {item.timeframe}
                      {scanData.best?.timeframe === item.timeframe && " ★"}
                    </span>
                    <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
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
            )}
          </>
        )}

      </div>
    </div>
  );
}
