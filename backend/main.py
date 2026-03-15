from datetime import datetime, timezone
import json
import os
import time
import pandas as pd
import pandas_ta as ta
import ccxt
import yfinance as yf

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ASSET_CONFIG = {
    "Bitcoin OTC":                  {"source": "binance", "ticker": "BTC/USDT"},
    "Bitcoin ETF OTC":              {"source": "binance", "ticker": "BTC/USDT"},
    "Ethereum OTC":                 {"source": "binance", "ticker": "ETH/USDT"},
    "Litecoin OTC":                 {"source": "binance", "ticker": "LTC/USDT"},
    "Solana OTC":                   {"source": "binance", "ticker": "SOL/USDT"},
    "Cardano OTC":                  {"source": "binance", "ticker": "ADA/USDT"},
    "BNB OTC":                      {"source": "binance", "ticker": "BNB/USDT"},
    "Dogecoin OTC":                 {"source": "binance", "ticker": "DOGE/USDT"},
    "Avalanche OTC":                {"source": "binance", "ticker": "AVAX/USDT"},
    "TRON OTC":                     {"source": "binance", "ticker": "TRX/USDT"},
    "Chainlink OTC":                {"source": "binance", "ticker": "LINK/USDT"},
    "Polkadot OTC":                 {"source": "binance", "ticker": "DOT/USDT"},
    "Polygon OTC":                  {"source": "binance", "ticker": "MATIC/USDT"},
    "Toncoin OTC":                  {"source": "binance", "ticker": "TON/USDT"},
    "EUR/USD OTC":                  {"source": "yahoo", "ticker": "EURUSD=X"},
    "GBP/USD OTC":                  {"source": "yahoo", "ticker": "GBPUSD=X"},
    "AUD/USD OTC":                  {"source": "yahoo", "ticker": "AUDUSD=X"},
    "USD/JPY OTC":                  {"source": "yahoo", "ticker": "USDJPY=X"},
    "USD/CAD OTC":                  {"source": "yahoo", "ticker": "USDCAD=X"},
    "USD/CHF OTC":                  {"source": "yahoo", "ticker": "USDCHF=X"},
    "NZD/USD OTC":                  {"source": "yahoo", "ticker": "NZDUSD=X"},
    "EUR/GBP OTC":                  {"source": "yahoo", "ticker": "EURGBP=X"},
    "EUR/JPY OTC":                  {"source": "yahoo", "ticker": "EURJPY=X"},
    "GBP/JPY OTC":                  {"source": "yahoo", "ticker": "GBPJPY=X"},
    "AUD/JPY OTC":                  {"source": "yahoo", "ticker": "AUDJPY=X"},
    "EUR/CHF OTC":                  {"source": "yahoo", "ticker": "EURCHF=X"},
    "USD/RUB OTC":                  {"source": "yahoo", "ticker": "USDRUB=X"},
    "EUR/RUB OTC":                  {"source": "yahoo", "ticker": "EURRUB=X"},
    "USD/MXN OTC":                  {"source": "yahoo", "ticker": "USDMXN=X"},
    "USD/BRL OTC":                  {"source": "yahoo", "ticker": "USDBRL=X"},
    "USD/INR OTC":                  {"source": "yahoo", "ticker": "USDINR=X"},
    "USD/CNH OTC":                  {"source": "yahoo", "ticker": "USDCNH=X"},
    "AUD/CAD OTC":                  {"source": "yahoo", "ticker": "AUDCAD=X"},
    "AUD/CHF OTC":                  {"source": "yahoo", "ticker": "AUDCHF=X"},
    "CAD/CHF OTC":                  {"source": "yahoo", "ticker": "CADCHF=X"},
    "CAD/JPY OTC":                  {"source": "yahoo", "ticker": "CADJPY=X"},
    "CHF/JPY OTC":                  {"source": "yahoo", "ticker": "CHFJPY=X"},
    "AUD/NZD OTC":                  {"source": "yahoo", "ticker": "AUDNZD=X"},
    "NZD/JPY OTC":                  {"source": "yahoo", "ticker": "NZDJPY=X"},
    "GBP/AUD OTC":                  {"source": "yahoo", "ticker": "GBPAUD=X"},
    "EUR/HUF OTC":                  {"source": "yahoo", "ticker": "EURHUF=X"},
    "EUR/TRY OTC":                  {"source": "yahoo", "ticker": "EURTRY=X"},
    "USD/SGD OTC":                  {"source": "yahoo", "ticker": "USDSGD=X"},
    "USD/THB OTC":                  {"source": "yahoo", "ticker": "USDTHB=X"},
    "USD/MYR OTC":                  {"source": "yahoo", "ticker": "USDMYR=X"},
    "Gold OTC":                     {"source": "yahoo", "ticker": "GC=F"},
    "Silver OTC":                   {"source": "yahoo", "ticker": "SI=F"},
    "Brent Oil OTC":                {"source": "yahoo", "ticker": "BZ=F"},
    "WTI Crude Oil OTC":            {"source": "yahoo", "ticker": "CL=F"},
    "Natural Gas OTC":              {"source": "yahoo", "ticker": "NG=F"},
    "Platinum spot OTC":            {"source": "yahoo", "ticker": "PL=F"},
    "Palladium spot OTC":           {"source": "yahoo", "ticker": "PA=F"},
    "Tesla OTC":                    {"source": "yahoo", "ticker": "TSLA"},
    "Apple OTC":                    {"source": "yahoo", "ticker": "AAPL"},
    "Amazon OTC":                   {"source": "yahoo", "ticker": "AMZN"},
    "Microsoft OTC":                {"source": "yahoo", "ticker": "MSFT"},
    "Netflix OTC":                  {"source": "yahoo", "ticker": "NFLX"},
    "FACEBOOK INC OTC":             {"source": "yahoo", "ticker": "META"},
    "Coinbase Global OTC":          {"source": "yahoo", "ticker": "COIN"},
    "Alibaba OTC":                  {"source": "yahoo", "ticker": "BABA"},
    "Intel OTC":                    {"source": "yahoo", "ticker": "INTC"},
    "Cisco OTC":                    {"source": "yahoo", "ticker": "CSCO"},
    "ExxonMobil OTC":               {"source": "yahoo", "ticker": "XOM"},
    "FedEx OTC":                    {"source": "yahoo", "ticker": "FDX"},
    "GameStop Corp OTC":            {"source": "yahoo", "ticker": "GME"},
    "Marathon Digital Holdings OTC":{"source": "yahoo", "ticker": "MARA"},
    "VISA OTC":                     {"source": "yahoo", "ticker": "V"},
    "VIX OTC":                      {"source": "yahoo", "ticker": "^VIX"},
    "Johnson & Johnson OTC":        {"source": "yahoo", "ticker": "JNJ"},
    "Palantir Technologies OTC":    {"source": "yahoo", "ticker": "PLTR"},
    "Citigroup Inc OTC":            {"source": "yahoo", "ticker": "C"},
    "American Express OTC":         {"source": "yahoo", "ticker": "AXP"},
    "Advanced Micro Devices OTC":   {"source": "yahoo", "ticker": "AMD"},
    "McDonald's OTC":               {"source": "yahoo", "ticker": "MCD"},
}

TIMEFRAME_MAP = {
    "M1":  {"binance": "1m",  "yahoo": "1m",  "yahoo_period": "1d"},
    "M3":  {"binance": "3m",  "yahoo": "5m",  "yahoo_period": "5d"},
    "M5":  {"binance": "5m",  "yahoo": "5m",  "yahoo_period": "5d"},
    "M10": {"binance": "15m", "yahoo": "15m", "yahoo_period": "5d"},
    "M15": {"binance": "15m", "yahoo": "15m", "yahoo_period": "5d"},
}

HIGHER_TIMEFRAME_MAP = {
    "M1":  {"binance": "5m",  "yahoo": "5m",  "yahoo_period": "5d"},
    "M3":  {"binance": "15m", "yahoo": "15m", "yahoo_period": "5d"},
    "M5":  {"binance": "15m", "yahoo": "15m", "yahoo_period": "5d"},
    "M10": {"binance": "1h",  "yahoo": "1h",  "yahoo_period": "1mo"},
    "M15": {"binance": "1h",  "yahoo": "1h",  "yahoo_period": "1mo"},
}

HISTORY_FILE     = "signals_history.json"
FOREX_OPEN_HOUR  = 8
FOREX_CLOSE_HOUR = 17
CACHE_TTL        = 30
_cache: dict     = {}


class SignalRequest(BaseModel):
    symbol: str
    timeframe: str = "M1"
    balance: str | None = None
    mode: str | None = "Уверенный"


def load_history() -> list:
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception:
            return []


def save_history(history: list):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def is_forex_open(symbol: str) -> bool:
    config = ASSET_CONFIG.get(symbol, {"source": "binance"})
    if config["source"] == "binance":
        return True
    now_utc = datetime.now(timezone.utc)
    if now_utc.weekday() >= 5:
        return False
    return FOREX_OPEN_HOUR <= now_utc.hour < FOREX_CLOSE_HOUR


def get_candles_binance(ticker: str, timeframe: str, limit: int = 150) -> pd.DataFrame:
    exchange = ccxt.binance({"enableRateLimit": True})
    raw = exchange.fetch_ohlcv(ticker, timeframe, limit=limit)
    df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df


def get_candles_yahoo(ticker: str, interval: str, period: str) -> pd.DataFrame:
    data = yf.download(ticker, interval=interval, period=period, progress=False)
    if data.empty:
        raise ValueError(f"Yahoo Finance не вернул данные для {ticker}")
    df = data.reset_index()
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    df = df.rename(columns={
        "Datetime": "timestamp", "Date": "timestamp",
        "Open": "open", "High": "high",
        "Low": "low", "Close": "close", "Volume": "volume"
    })
    df = df[["timestamp", "open", "high", "low", "close", "volume"]].copy()
    df.dropna(inplace=True)
    return df


def get_candles(symbol: str, timeframe: str, higher: bool = False) -> pd.DataFrame:
    cache_key = f"{symbol}_{timeframe}_{'h' if higher else 'l'}"
    now = time.time()
    if cache_key in _cache:
        cached_time, cached_df = _cache[cache_key]
        if now - cached_time < CACHE_TTL:
            return cached_df.copy()
    config    = ASSET_CONFIG.get(symbol, {"source": "binance", "ticker": "BTC/USDT"})
    tf_map    = HIGHER_TIMEFRAME_MAP if higher else TIMEFRAME_MAP
    tf_config = tf_map.get(timeframe, tf_map.get("M1"))
    if config["source"] == "binance":
        df = get_candles_binance(config["ticker"], tf_config["binance"])
    else:
        df = get_candles_yahoo(config["ticker"], tf_config["yahoo"], tf_config["yahoo_period"])
    _cache[cache_key] = (now, df.copy())
    return df


def get_current_price(symbol: str) -> float | None:
    try:
        config = ASSET_CONFIG.get(symbol, {"source": "binance", "ticker": "BTC/USDT"})
        if config["source"] == "binance":
            exchange = ccxt.binance({"enableRateLimit": True})
            return exchange.fetch_ticker(config["ticker"])["last"]
        else:
            data = yf.download(config["ticker"], period="1d", interval="1m", progress=False)
            if not data.empty:
                return float(data["Close"].iloc[-1])
    except Exception:
        return None


def get_higher_trend(df_higher: pd.DataFrame) -> str:
    df = df_higher.copy()
    df["ema9"]  = ta.ema(df["close"], length=9)
    df["ema21"] = ta.ema(df["close"], length=21)
    df.dropna(inplace=True)
    if df.empty:
        return "neutral"
    last = df.iloc[-1]
    if last["ema9"] > last["ema21"]:
        return "up"
    elif last["ema9"] < last["ema21"]:
        return "down"
    return "neutral"


def detect_candle_pattern(df: pd.DataFrame) -> tuple:
    if len(df) < 2:
        return "none", "neutral"
    curr = df.iloc[-1]
    prev = df.iloc[-2]
    body_curr  = abs(float(curr["close"]) - float(curr["open"]))
    range_curr = float(curr["high"]) - float(curr["low"])
    if range_curr == 0:
        return "none", "neutral"
    if body_curr / range_curr < 0.1:
        return "Doji (неопределённость)", "neutral"
    if (float(prev["close"]) < float(prev["open"]) and
            float(curr["close"]) > float(curr["open"]) and
            float(curr["close"]) > float(prev["open"]) and
            float(curr["open"]) < float(prev["close"])):
        return "Бычье поглощение", "up"
    if (float(prev["close"]) > float(prev["open"]) and
            float(curr["close"]) < float(curr["open"]) and
            float(curr["close"]) < float(prev["open"]) and
            float(curr["open"]) > float(prev["close"])):
        return "Медвежье поглощение", "down"
    lower_shadow = float(min(curr["open"], curr["close"])) - float(curr["low"])
    upper_shadow = float(curr["high"]) - float(max(curr["open"], curr["close"]))
    if lower_shadow > body_curr * 2 and upper_shadow < body_curr * 0.5:
        return "Молот (разворот вверх)", "up"
    if upper_shadow > body_curr * 2 and lower_shadow < body_curr * 0.5:
        return "Падающая звезда (разворот вниз)", "down"
    return "none", "neutral"


def analyze(df: pd.DataFrame, higher_trend: str = "neutral", mode: str = "Уверенный") -> dict:
    df = df.copy()
    df["ema9"]   = ta.ema(df["close"], length=9)
    df["ema21"]  = ta.ema(df["close"], length=21)
    df["rsi"]    = ta.rsi(df["close"], length=14)
    df["atr"]    = ta.atr(df["high"], df["low"], df["close"], length=14)
    df["mom"]    = df["close"] - df["close"].shift(10)
    df["vol_ma"] = df["volume"].rolling(20).mean()

    macd = ta.macd(df["close"], fast=12, slow=26, signal=9)
    df["macd"]        = macd["MACD_12_26_9"]
    df["macd_signal"] = macd["MACDs_12_26_9"]
    df["macd_hist"]   = macd["MACDh_12_26_9"]

    bb = ta.bbands(df["close"], length=20, std=2)
    bb_cols   = bb.columns.tolist()
    upper_col = [c for c in bb_cols if "BBU" in c]
    lower_col = [c for c in bb_cols if "BBL" in c]
    mid_col   = [c for c in bb_cols if "BBM" in c]
    if upper_col and lower_col and mid_col:
        df["bb_upper"] = bb[upper_col[0]]
        df["bb_lower"] = bb[lower_col[0]]
        df["bb_mid"]   = bb[mid_col[0]]
        has_bb = True
    else:
        has_bb = False

    df.dropna(inplace=True)

    if df.empty:
        return {"signal": "NO SIGNAL", "confidence": 0,
                "reasons": ["Недостаточно данных"], "state": "neutral",
                "entry_price": None}

    last = df.iloc[-1]

    if (float(last["atr"]) / float(last["close"])) < 0.0003:
        return {"signal": "NO SIGNAL", "confidence": 0,
                "reasons": ["Рынок в боковике"], "state": "neutral",
                "entry_price": float(last["close"])}

    rsi_val = float(last["rsi"])
    if rsi_val > 75 or rsi_val < 25:
        return {"signal": "NO SIGNAL", "confidence": 0,
                "reasons": [f"RSI в экстремальной зоне ({rsi_val:.0f})"],
                "state": "neutral", "entry_price": float(last["close"])}

    if mode == "Новичок":
        min_conditions = 5
        min_confidence = 70
    elif mode == "Про":
        min_conditions = 2
        min_confidence = 0
    else:
        min_conditions = 3
        min_confidence = 55

    up_blocked   = higher_trend == "down"
    down_blocked = higher_trend == "up"

    pattern_name, pattern_dir = detect_candle_pattern(df)

    if has_bb:
        bb_near_lower = float(last["close"]) <= float(last["bb_lower"]) * 1.005
        bb_near_upper = float(last["close"]) >= float(last["bb_upper"]) * 0.995
        bb_above_mid  = float(last["close"]) > float(last["bb_mid"])
        bb_below_mid  = float(last["close"]) < float(last["bb_mid"])
    else:
        bb_near_lower = bb_near_upper = bb_above_mid = bb_below_mid = False

    bullish_candle = float(last["close"]) > float(last["open"])
    bearish_candle = float(last["close"]) < float(last["open"])
    macd_bullish   = float(last["macd"]) > float(last["macd_signal"]) and float(last["macd_hist"]) > 0
    macd_bearish   = float(last["macd"]) < float(last["macd_signal"]) and float(last["macd_hist"]) < 0
    vol_bonus      = 10 if float(last["volume"]) > float(last["vol_ma"]) else 0

    up_checks = [
        (float(last["ema9"]) > float(last["ema21"]), "Быстрая EMA выше медленной"),
        (40 < rsi_val < 65,                           f"RSI в бычьей зоне ({rsi_val:.0f})"),
        (float(last["mom"]) > 0,                      "Импульс положительный"),
        (macd_bullish,                                "MACD подтверждает рост"),
        (bullish_candle,                              "Свеча бычья"),
        (bb_near_lower or bb_above_mid,               "Bollinger: зона роста"),
        (pattern_dir == "up",                         f"Паттерн: {pattern_name}"),
    ]

    down_checks = [
        (float(last["ema9"]) < float(last["ema21"]), "Быстрая EMA ниже медленной"),
        (35 < rsi_val < 60,                           f"RSI в медвежьей зоне ({rsi_val:.0f})"),
        (float(last["mom"]) < 0,                      "Импульс отрицательный"),
        (macd_bearish,                                "MACD подтверждает падение"),
        (bearish_candle,                              "Свеча медвежья"),
        (bb_near_upper or bb_below_mid,               "Bollinger: зона падения"),
        (pattern_dir == "down",                       f"Паттерн: {pattern_name}"),
    ]

    up_met   = [(v, r) for v, r in up_checks   if v]
    down_met = [(v, r) for v, r in down_checks if v]

    if len(up_met) >= min_conditions and len(up_met) >= len(down_met) and not up_blocked:
        confidence = min(int(len(up_met) / 7 * 100) + vol_bonus, 95)
        if confidence < min_confidence:
            return {"signal": "NO SIGNAL", "confidence": 0,
                    "reasons": ["Сигнал слабый для режима " + mode],
                    "state": "neutral", "entry_price": float(last["close"])}
        reasons = [r for _, r in up_met]
        if higher_trend == "up":
            reasons.append("Тренд старшего ТФ подтверждает рост")
        return {"signal": "UP", "confidence": confidence,
                "reasons": reasons, "state": "bullish",
                "entry_price": float(last["close"])}

    if len(down_met) >= min_conditions and len(down_met) > len(up_met) and not down_blocked:
        confidence = min(int(len(down_met) / 7 * 100) + vol_bonus, 95)
        if confidence < min_confidence:
            return {"signal": "NO SIGNAL", "confidence": 0,
                    "reasons": ["Сигнал слабый для режима " + mode],
                    "state": "neutral", "entry_price": float(last["close"])}
        reasons = [r for _, r in down_met]
        if higher_trend == "down":
            reasons.append("Тренд старшего ТФ подтверждает падение")
        return {"signal": "DOWN", "confidence": confidence,
                "reasons": reasons, "state": "bearish",
                "entry_price": float(last["close"])}

    return {"signal": "NO SIGNAL", "confidence": 0,
            "reasons": ["Недостаточно подтверждений"], "state": "neutral",
            "entry_price": float(last["close"])}


def update_win_rate(history: list, symbol: str) -> list:
    now = datetime.now(timezone.utc)
    current_price = get_current_price(symbol)
    if current_price is None:
        return history
    for entry in history:
        if entry.get("result") is not None:
            continue
        if entry.get("signal") == "NO SIGNAL":
            entry["result"] = "skip"
            continue
        if entry.get("entry_price") is None:
            continue
        try:
            signal_time = datetime.fromisoformat(entry["timestamp"])
            if signal_time.tzinfo is None:
                signal_time = signal_time.replace(tzinfo=timezone.utc)
        except Exception:
            continue
        if (now - signal_time).total_seconds() < 300:
            continue
        entry_price = entry["entry_price"]
        if entry["signal"] == "UP":
            entry["result"] = "WIN" if current_price > entry_price else "LOSS"
        elif entry["signal"] == "DOWN":
            entry["result"] = "WIN" if current_price < entry_price else "LOSS"
        entry["exit_price"] = current_price
    return history


def calc_win_rate(history: list) -> float:
    finished = [e for e in history if e.get("result") in ("WIN", "LOSS")]
    if not finished:
        return 0.0
    wins = sum(1 for e in finished if e["result"] == "WIN")
    return round(wins / len(finished) * 100, 1)


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/history")
def get_history():
    history = load_history()
    return {
        "history":  history[-20:],
        "win_rate": calc_win_rate(history),
        "total":    len(history),
    }


@app.post("/signal")
def get_signal(payload: SignalRequest):
    if not is_forex_open(payload.symbol):
        result = {
            "signal":      "NO SIGNAL",
            "confidence":  0,
            "reasons":     ["Рынок закрыт — форекс работает пн-пт 08:00-17:00 UTC"],
            "state":       "neutral",
            "entry_price": None,
        }
    else:
        try:
            df = get_candles(payload.symbol, payload.timeframe, higher=False)
            try:
                df_higher    = get_candles(payload.symbol, payload.timeframe, higher=True)
                higher_trend = get_higher_trend(df_higher)
            except Exception:
                higher_trend = "neutral"
            result = analyze(df, higher_trend, payload.mode or "Уверенный")
        except Exception as e:
            result = {
                "signal":      "NO SIGNAL",
                "confidence":  0,
                "reasons":     [f"Ошибка: {str(e)}"],
                "state":       "neutral",
                "entry_price": None,
            }

    history = load_history()
    history = update_win_rate(history, payload.symbol)
    history.append({
        "signal":      result["signal"],
        "confidence":  result["confidence"],
        "reasons":     result["reasons"],
        "state":       result["state"],
        "entry_price": result.get("entry_price"),
        "exit_price":  None,
        "result":      None,
        "symbol":      payload.symbol,
        "timeframe":   payload.timeframe,
        "timestamp":   datetime.utcnow().isoformat(),
    })
    history = history[-100:]
    save_history(history)

    return {
        "signal":      result["signal"],
        "confidence":  result["confidence"],
        "reasons":     result["reasons"],
        "state":       result["state"],
        "entry_price": result.get("entry_price"),
        "symbol":      payload.symbol,
        "timeframe":   payload.timeframe,
        "balance":     payload.balance,
        "mode":        payload.mode,
        "timestamp":   datetime.utcnow().isoformat(),
        "win_rate":    calc_win_rate(history),
    }


@app.post("/scan")
def scan_all_timeframes(payload: SignalRequest):
    """AI Сканер — анализирует все таймфреймы сразу."""
    if not is_forex_open(payload.symbol):
        return {
            "results": [],
            "best":    None,
            "reason":  "Рынок закрыт — форекс работает пн-пт 08:00-17:00 UTC"
        }

    timeframes_to_scan = ["M1", "M3", "M5", "M10", "M15"]
    results = []

    for tf in timeframes_to_scan:
        try:
            df = get_candles(payload.symbol, tf, higher=False)
            try:
                df_higher    = get_candles(payload.symbol, tf, higher=True)
                higher_trend = get_higher_trend(df_higher)
            except Exception:
                higher_trend = "neutral"
            result = analyze(df, higher_trend, payload.mode or "Уверенный")
            results.append({
                "timeframe":  tf,
                "signal":     result["signal"],
                "confidence": result["confidence"],
                "reasons":    result["reasons"],
                "state":      result["state"],
            })
        except Exception as e:
            results.append({
                "timeframe":  tf,
                "signal":     "ERROR",
                "confidence": 0,
                "reasons":    [str(e)],
                "state":      "neutral",
            })

    # Лучший таймфрейм — максимальная уверенность среди UP/DOWN
    real_signals = [r for r in results if r["signal"] in ("UP", "DOWN")]

    if real_signals:
        best = max(real_signals, key=lambda x: x["confidence"])
        same_direction = [r for r in real_signals if r["signal"] == best["signal"]]
        agreement = len(same_direction)
        best_reason = (
            f"Лучший вход — {best['timeframe']} "
            f"({best['signal']} {best['confidence']}%). "
            f"{agreement} из {len(results)} таймфреймов согласны. "
            f"Ключевые причины: {', '.join(best['reasons'][:2])}"
        )
    else:
        best = None
        best_reason = "Ни на одном таймфрейме нет чёткого сигнала — лучше подождать"

    return {
        "results": results,
        "best":    best,
        "reason":  best_reason,
    }