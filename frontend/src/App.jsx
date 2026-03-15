import "./App.css";
import { useState, useEffect, useRef } from "react";

export default function App() {
  const [signalData, setSignalData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [symbol, setSymbol] = useState("Bitcoin OTC");
  const [timeframe, setTimeframe] = useState("M1");
  const [mode, setMode] = useState("Уверенный");
  const [signalCount, setSignalCount] = useState(0);
  const [history, setHistory] = useState([]);
  const [historyOpen, setHistoryOpen] = useState(true);
  const [autoInterval, setAutoInterval] = useState(30);
  const [autoRunning, setAutoRunning] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const [scanData, setScanData] = useState(null);
  const [scanLoading, setScanLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("manual");

  const intervalRef  = useRef(null);
  const countdownRef = useRef(null);
  const loadingRef   = useRef(false);

  const symbols = [
    "EUR/USD OTC", "GBP/USD OTC", "AUD/USD OTC", "USD/JPY OTC",
    "USD/CAD OTC", "USD/CHF OTC", "NZD/USD OTC", "EUR/GBP OTC",
    "EUR/JPY OTC", "GBP/JPY OTC", "AUD/JPY OTC", "EUR/CHF OTC",
    "USD/RUB OTC", "EUR/RUB OTC", "USD/MXN OTC", "USD/BRL OTC",
    "USD/INR OTC", "USD/CNH OTC", "AUD/CAD OTC", "AUD/CHF OTC",
    "CAD/CHF OTC", "CAD/JPY OTC", "CHF/JPY OTC", "AUD/NZD OTC",
    "NZD/JPY OTC", "GBP/AUD OTC", "EUR/HUF OTC", "EUR/TRY OTC",
    "USD/SGD OTC", "USD/THB OTC", "USD/MYR OTC",
    "Bitcoin OTC", "Bitcoin ETF OTC", "Ethereum OTC", "Litecoin OTC",
    "Solana OTC", "Cardano OTC", "BNB OTC", "Dogecoin OTC",
    "Avalanche OTC", "TRON OTC", "Chainlink OTC", "Polkadot OTC",
    "Polygon OTC", "Toncoin OTC",
    "Gold OTC", "Silver OTC", "Brent Oil OTC", "WTI Crude Oil OTC",
    "Natural Gas OTC", "Platinum spot OTC", "Palladium spot OTC",
    "Tesla OTC", "Apple OTC", "Amazon OTC", "Microsoft OTC",
    "Netflix OTC", "FACEBOOK INC OTC", "Coinbase Global OTC",
    "Alibaba OTC", "Intel OTC", "Cisco OTC", "ExxonMobil OTC",
    "FedEx OTC", "GameStop Corp OTC", "Marathon Digital Holdings OTC",
    "VISA OTC", "VIX OTC", "Johnson & Johnson OTC",
    "Palantir Technologies OTC", "Citigroup Inc OTC",
    "American Express OTC", "Advanced Micro Devices OTC", "McDonald's OTC",
  ];

  const timeframes = ["M1", "M3", "M5", "M10", "M15"];
  const modes = ["Новичок", "Уверенный", "Про"];
  const autoIntervals = [
    { label: "10 сек", value: 10 },
    { label: "30 сек", value: 30 },
    { label: "1 мин",  value: 60 },
    { label: "3 мин",  value: 180 },
    { label: "5 мин",  value: 300 },
  ];

  function playSignalSound(type) {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      if (type === "UP") {
        [0, 0.15].forEach((delay, i) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.connect(gain); gain.connect(ctx.destination);
          osc.frequency.value = i === 0 ? 520 : 780;
          osc.type = "sine";
          gain.gain.setValueAtTime(0.3, ctx.currentTime + delay);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + delay + 0.4);
          osc.start(ctx.currentTime + delay);
          osc.stop(ctx.currentTime + delay + 0.4);
        });
      } else if (type === "DOWN") {
        [0, 0.15].forEach((delay, i) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.connect(gain); gain.connect(ctx.destination);
          osc.frequency.value = i === 0 ? 780 : 520;
          osc.type = "sine";
          gain.gain.setValueAtTime(0.3, ctx.currentTime + delay);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + delay + 0.4);
          osc.start(ctx.currentTime + delay);
          osc.stop(ctx.currentTime + delay + 0.4);
        });
      }
    } catch (e) {}
  }

  function stopAuto() {
    clearInterval(intervalRef.current);
    clearInterval(countdownRef.current);
    setAutoRunning(false);
    setCountdown(0);
  }

  async function fetchSignal(isAuto = false) {
    if (loadingRef.current) return;
    loadingRef.current = true;
    setLoading(true);
    try {
      const response = await fetch("http://127.0.0.1:8000/signal", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol, timeframe, mode }),
      });
      const data = await response.json();
      setSignalData(data);
      setSignalCount((prev) => prev + 1);
      setHistory((prev) =>
        [{ signal: data.signal, confidence: data.confidence,
           symbol: data.symbol, timeframe: data.timeframe,
           time: new Date(data.timestamp).toLocaleTimeString("ru-RU") },
         ...prev].slice(0, 10)
      );
      if (isAuto && (data.signal === "UP" || data.signal === "DOWN")) {
        playSignalSound(data.signal);
        stopAuto();
      }
    } catch (error) {
      setSignalData({ signal: "ERROR", confidence: 0,
        reasons: ["Не удалось получить сигнал"], state: "neutral",
        symbol, timeframe, mode, timestamp: new Date().toISOString() });
      setSignalCount((prev) => prev + 1);
    } finally {
      loadingRef.current = false;
      setLoading(false);
    }
  }

  async function fetchScan() {
    setScanLoading(true);
    setScanData(null);
    try {
      const response = await fetch("http://127.0.0.1:8000/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol, timeframe: "M1", mode }),
      });
      const data = await response.json();
      setScanData(data);
      if (data.best) playSignalSound(data.best.signal);
    } catch (error) {
      setScanData({ results: [], best: null, reason: "Ошибка подключения" });
    } finally {
      setScanLoading(false);
    }
  }

  function startAuto() {
    fetchSignal(true);
    setCountdown(autoInterval);
    setAutoRunning(true);
    countdownRef.current = setInterval(() => {
      setCountdown((prev) => (prev <= 1 ? autoInterval : prev - 1));
    }, 1000);
    intervalRef.current = setInterval(() => fetchSignal(true), autoInterval * 1000);
  }

  useEffect(() => { if (autoRunning) stopAuto(); }, [symbol, timeframe, mode]);
  useEffect(() => {// Загружаем историю и Win Rate при старте
useEffect(() => {
  fetch("http://127.0.0.1:8000/history")
    .then((r) => r.json())
    .then((data) => {
      if (data.history && data.history.length > 0) {
        setHistory(
          data.history
            .filter((h) => h.signal !== "NO SIGNAL")
            .slice(-10)
            .reverse()
            .map((h) => ({
              signal:     h.signal,
              confidence: h.confidence,
              symbol:     h.symbol,
              timeframe:  h.timeframe,
              time:       new Date(h.timestamp).toLocaleTimeString("ru-RU"),
            }))
        );
        setSignalCount(data.total || 0);
        // Обновляем Win Rate
        if (data.win_rate != null) {
          setSignalData((prev) =>
            prev ? { ...prev, win_rate: data.win_rate } : { win_rate: data.win_rate }
          );
        }
      }
    })
    .catch(() => {});
}, []);

    return () => {
      clearInterval(intervalRef.current);
      clearInterval(countdownRef.current);
    };
  }, []);

  const signalColor = (signal) => {
    if (signal === "UP")   return "#00c896";
    if (signal === "DOWN") return "#ff4f5e";
    return "#888";
  };

  return (
    <div className="app">
      <div className="phone-shell">

        {/* Шапка */}
        <div className="top-card">
          <div>
            <div className="asset-title">{symbol}</div>
            <div className="sub-text">
              {new Date().toLocaleTimeString("ru-RU")}
              {activeTab === "manual" ? ` · ${timeframe}` : " · AI сканер"}
            </div>
          </div>
          <div className="badge">{autoRunning ? "🔍 Ищу..." : "Готов"}</div>
        </div>

        {/* Статистика */}
        <div className="stats-card">
          <div className="stat-item">
            <span>Win Rate</span>
            <strong>{signalData?.win_rate != null ? signalData.win_rate + "%" : "0%"}</strong>
          </div>
          <div className="stat-item">
            <span>Сигналы</span>
            <strong>{signalCount}</strong>
          </div>
          <div className="stat-item">
            <span>Режим</span>
            <strong>{activeTab === "manual" ? mode : "AI"}</strong>
          </div>
          <div className="stat-item">
            <span>Таймфрейм</span>
            <strong>{activeTab === "manual" ? timeframe : "все"}</strong>
          </div>
        </div>

        {/* Актив — общий для обоих вкладок */}
        <div className="card">
          <label className="label">Актив</label>
          <select className="input" value={symbol}
            onChange={(e) => setSymbol(e.target.value)}>
            {symbols.map((item) => (
              <option key={item} value={item}>{item}</option>
            ))}
          </select>
        </div>

        {/* Вкладки */}
        <div style={{ display: "flex", gap: "8px", margin: "4px 0 8px" }}>
          <button onClick={() => setActiveTab("manual")} style={{
            flex: 1, padding: "10px", borderRadius: "10px", border: "none",
            background: activeTab === "manual" ? "var(--primary,#3b82f6)" : "var(--card-bg,#1e2435)",
            color: "#fff", fontWeight: "600", cursor: "pointer", fontSize: "13px",
          }}>
            ручной
          </button>
          <button onClick={() => setActiveTab("scanner")} style={{
            flex: 1, padding: "10px", borderRadius: "10px", border: "none",
            background: activeTab === "scanner" ? "var(--primary,#3b82f6)" : "var(--card-bg,#1e2435)",
            color: "#fff", fontWeight: "600", cursor: "pointer", fontSize: "13px",
          }}>
            🤖 AI сканер
          </button>
        </div>

        {/* РУЧНОЙ РЕЖИМ */}
        {activeTab === "manual" && (
          <>
            {/* Таймфрейм */}
            <div className="card">
              <label className="label">Таймфрейм</label>
              <div className="timeframe-row">
                {timeframes.map((item) => (
                  <button key={item}
                    className={"time-btn" + (timeframe === item ? " active" : "")}
                    onClick={() => setTimeframe(item)}>{item}</button>
                ))}
              </div>
            </div>

            {/* Режим */}
            <div className="mode-card">
              {modes.map((item) => (
                <button key={item}
                  className={"mode-btn" + (mode === item ? " active" : "")}
                  onClick={() => setMode(item)}>{item}</button>
              ))}
            </div>

            {/* Автоанализ */}
            <div className="card">
              <label className="label">Интервал автоанализа</label>
              <div className="timeframe-row" style={{ marginBottom: "10px" }}>
                {autoIntervals.map((item) => (
                  <button key={item.value}
                    className={"time-btn" + (autoInterval === item.value ? " active" : "")}
                    onClick={() => { if (!autoRunning) setAutoInterval(item.value); }}
                    disabled={autoRunning}>{item.label}</button>
                ))}
              </div>
              <button className="main-button"
                style={{ background: autoRunning ? "#e53e3e" : undefined }}
                onClick={autoRunning ? stopAuto : startAuto}>
                {autoRunning
                  ? `⏹ СТОП (через ${countdown} сек)`
                  : "🔍 ИСКАТЬ СИГНАЛ АВТО"}
              </button>
            </div>

            <div className="ready-card">
              {autoRunning
                ? `🔍 Ищу сигнал каждые ${autoInterval} сек — остановлюсь когда найду`
                : "ГОТОВ К АНАЛИЗУ"}
            </div>

            <button className="main-button"
              onClick={() => fetchSignal(false)} disabled={loading}
              style={{ opacity: autoRunning ? 0.6 : 1 }}>
              {loading ? "АНАЛИЗ..." : "ПОЛУЧИТЬ СИГНАЛ"}
            </button>

            {/* Результат */}
            <div className="result-card">
              <div className="result-header">
                <span>Результат</span>
                <span className={"signal-pill " + (signalData ? signalData.state : "neutral")}>
                  {signalData ? signalData.signal : "ОЖИДАНИЕ"}
                </span>
              </div>
              <div className="result-body">
                <div className="result-row">
                  <span>Уверенность</span>
                  <strong>{signalData ? signalData.confidence + "%" : "--"}</strong>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill"
                    style={{ width: (signalData ? signalData.confidence : 0) + "%" }} />
                </div>
                <div className="result-row">
                  <span>Актив</span>
                  <strong>{signalData ? signalData.symbol : symbol}</strong>
                </div>
                <div className="result-row">
                  <span>Таймфрейм</span>
                  <strong>{signalData ? signalData.timeframe : timeframe}</strong>
                </div>
                <div className="result-row">
                  <span>Режим</span>
                  <strong>{signalData ? signalData.mode : mode}</strong>
                </div>
                <div className="result-row">
                  <span>Цена входа</span>
                  <strong>
                    {signalData?.entry_price
                      ? Number(signalData.entry_price).toFixed(2) : "--"}
                  </strong>
                </div>
                <div className="reasons-block">
                  <div className="label">Причины</div>
                  <ul>
                    {signalData?.reasons?.length > 0
                      ? signalData.reasons.map((r, i) => <li key={i}>{r}</li>)
                      : <li>Сигнал еще не запрошен</li>}
                  </ul>
                </div>
                <div className="time-stamp">
                  {signalData?.timestamp
                    ? "Время: " + new Date(signalData.timestamp).toLocaleString("ru-RU")
                    : "Время: --"}
                </div>
              </div>
            </div>
          </>
        )}

        {/* AI СКАНЕР */}
        {activeTab === "scanner" && (
          <>
            <div className="ready-card">
              🤖 AI сканер проверит все таймфреймы и выберет лучший вход
            </div>

            <button className="main-button" onClick={fetchScan} disabled={scanLoading}>
              {scanLoading ? "🔍 СКАНИРУЮ ВСЕ ТАЙМФРЕЙМЫ..." : "🤖 ЗАПУСТИТЬ AI СКАНЕР"}
            </button>

            {scanData && (
              <div className="result-card">
                {scanData.best ? (
                  <div style={{
                    background: scanData.best.signal === "UP"
                      ? "rgba(0,200,150,0.1)" : "rgba(255,79,94,0.1)",
                    border: `1px solid ${signalColor(scanData.best.signal)}`,
                    borderRadius: "12px", padding: "16px", marginBottom: "16px",
                  }}>
                    <div style={{ fontSize: "12px", opacity: 0.7, marginBottom: "4px" }}>
                      🏆 Лучший вход
                    </div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <div>
                        <span style={{ fontSize: "22px", fontWeight: "700",
                          color: signalColor(scanData.best.signal) }}>
                          {scanData.best.signal}
                        </span>
                        <span style={{ fontSize: "16px", marginLeft: "8px", fontWeight: "600" }}>
                          {scanData.best.timeframe}
                        </span>
                      </div>
                      <span style={{ fontSize: "20px", fontWeight: "700",
                        color: signalColor(scanData.best.signal) }}>
                        {scanData.best.confidence}%
                      </span>
                    </div>
                    <div style={{ fontSize: "12px", opacity: 0.8, marginTop: "8px" }}>
                      {scanData.reason}
                    </div>
                  </div>
                ) : (
                  <div style={{
                    background: "rgba(136,136,136,0.1)", borderRadius: "12px",
                    padding: "16px", marginBottom: "16px", textAlign: "center",
                    fontSize: "13px", opacity: 0.8
                  }}>
                    {scanData.reason}
                  </div>
                )}

                <div className="label" style={{ marginBottom: "8px" }}>Все таймфреймы</div>
                {scanData.results.map((item, index) => (
                  <div key={index} style={{
                    display: "flex", justifyContent: "space-between", alignItems: "center",
                    padding: "10px 0",
                    borderBottom: index < scanData.results.length - 1
                      ? "1px solid rgba(255,255,255,0.06)" : "none",
                  }}>
                    <span style={{ fontWeight: "700", fontSize: "14px",
                      color: scanData.best?.timeframe === item.timeframe
                        ? signalColor(item.signal) : "inherit" }}>
                      {item.timeframe}
                      {scanData.best?.timeframe === item.timeframe && " 🏆"}
                    </span>
                    <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
                      <span style={{ fontSize: "13px", fontWeight: "600",
                        color: signalColor(item.signal) }}>
                        {item.signal}
                      </span>
                      <span style={{ fontSize: "13px", fontWeight: "600",
                        color: item.confidence > 0 ? signalColor(item.signal) : "#888" }}>
                        {item.confidence > 0 ? item.confidence + "%" : "--"}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {/* История */}
        <div className="result-card">
          <div className="result-header"
            onClick={() => setHistoryOpen((prev) => !prev)}
            style={{ cursor: "pointer", userSelect: "none" }}>
            <span>История сигналов</span>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span className="signal-pill neutral">{history.length}</span>
              <span style={{ fontSize: "12px", opacity: 0.6 }}>
                {historyOpen ? "▲ свернуть" : "▼ развернуть"}
              </span>
            </div>
          </div>
          {historyOpen && (
            <div className="result-body">
              {history.length === 0 ? (
                <div className="time-stamp">История пока пуста</div>
              ) : (
                history.map((item, index) => (
                  <div className="history-item" key={index}>
                    <div>
                      <strong>{item.signal}</strong>
                      <div className="time-stamp">{item.symbol} · {item.timeframe}</div>
                    </div>
                    <div className="history-right">
                      <strong>{item.confidence}%</strong>
                      <div className="time-stamp">{item.time}</div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>

      </div>
    </div>
  );
}