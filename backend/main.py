from datetime import datetime, timezone, timedelta
import json
import os
import time
import pandas as pd
import pandas_ta as ta
import ccxt
from tvdatafeed import TvDatafeed, Interval

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
    # Форекс
    "EUR/USD":   {"source": "tv", "symbol": "EURUSD",     "exchange": "FX"},
    "GBP/USD":   {"source": "tv", "symbol": "GBPUSD",     "exchange": "FX"},
    "AUD/USD":   {"source": "tv", "symbol": "AUDUSD",     "exchange": "FX"},
    "USD/JPY":   {"source": "tv", "symbol": "USDJPY",     "exchange": "FX"},
    "USD/CAD":   {"source": "tv", "symbol": "USDCAD",     "exchange": "FX"},
    "USD/CHF":   {"source": "tv", "symbol": "USDCHF",     "exchange": "FX"},
    "EUR/GBP":   {"source": "tv", "symbol": "EURGBP",     "exchange": "FX"},
    "EUR/JPY":   {"source": "tv", "symbol": "EURJPY",     "exchange": "FX"},
    "EUR/CHF":   {"source": "tv", "symbol": "EURCHF",     "exchange": "FX"},
    "EUR/AUD":   {"source": "tv", "symbol": "EURAUD",     "exchange": "FX"},
    "EUR/CAD":   {"source": "tv", "symbol": "EURCAD",     "exchange": "FX"},
    "GBP/JPY":   {"source": "tv", "symbol": "GBPJPY",     "exchange": "FX"},
    "GBP/CHF":   {"source": "tv", "symbol": "GBPCHF",     "exchange": "FX"},
    "GBP/AUD":   {"source": "tv", "symbol": "GBPAUD",     "exchange": "FX"},
    "GBP/CAD":   {"source": "tv", "symbol": "GBPCAD",     "exchange": "FX"},
    "AUD/JPY":   {"source": "tv", "symbol": "AUDJPY",     "exchange": "FX"},
    "AUD/CAD":   {"source": "tv", "symbol": "AUDCAD",     "exchange": "FX"},
    "AUD/CHF":   {"source": "tv", "symbol": "AUDCHF",     "exchange": "FX"},
    "CAD/JPY":   {"source": "tv", "symbol": "CADJPY",     "exchange": "FX"},
    "CAD/CHF":   {"source": "tv", "symbol": "CADCHF",     "exchange": "FX"},
    "CHF/JPY":   {"source": "tv", "symbol": "CHFJPY",     "exchange": "FX"},
    "NZD/USD":   {"source": "tv", "symbol": "NZDUSD",     "exchange": "FX"},
    "NZD/JPY":   {"source": "tv", "symbol": "NZDJPY",     "exchange": "FX"},
    "NZD/CAD":   {"source": "tv", "symbol": "NZDCAD",     "exchange": "FX"},
    "NZD/CHF":   {"source": "tv", "symbol": "NZDCHF",     "exchange": "FX"},
    "NZD/GBP":   {"source": "tv", "symbol": "NZDGBP",     "exchange": "FX"},
    # Крипто
    "Bitcoin":        {"source": "binance", "ticker": "BTC/USDT"},
    "Ethereum":       {"source": "binance", "ticker": "ETH/USDT"},
    "Dash":           {"source": "binance", "ticker": "DASH/USDT"},
    "Chainlink":      {"source": "binance", "ticker": "LINK/USDT"},
    "Bitcoin Cash":   {"source": "binance", "ticker": "BCH/USDT"},
    # Акции
    "Apple":          {"source": "tv", "symbol": "AAPL",  "exchange": "NASDAQ"},
    "Microsoft":      {"source": "tv", "symbol": "MSFT",  "exchange": "NASDAQ"},
    "Tesla":          {"source": "tv", "symbol": "TSLA",  "exchange": "NASDAQ"},
    "Netflix":        {"source": "tv", "symbol": "NFLX",  "exchange": "NASDAQ"},
    "Amazon":         {"source": "tv", "symbol": "AMZN",  "exchange": "NASDAQ"},
    "Google":         {"source": "tv", "symbol": "GOOGL", "exchange": "NASDAQ"},
    "Meta":           {"source": "tv", "symbol": "META",  "exchange": "NASDAQ"},
    "Intel":          {"source": "tv", "symbol": "INTC",  "exchange": "NASDAQ"},
    "Cisco":          {"source": "tv", "symbol": "CSCO",  "exchange": "NASDAQ"},
    "ExxonMobil":     {"source": "tv", "symbol": "XOM",   "exchange": "NYSE"},
    "Johnson & Johnson": {"source": "tv", "symbol": "JNJ", "exchange": "NYSE"},
    "Pfizer":         {"source": "tv", "symbol": "PFE",   "exchange": "NYSE"},
    "Boeing":         {"source": "tv", "symbol": "BA",    "exchange": "NYSE"},
    "McDonald's":     {"source": "tv", "symbol": "MCD",   "exchange": "NYSE"},
    "JPMorgan":       {"source": "tv", "symbol": "JPM",   "exchange": "NYSE"},
    "American Express": {"source": "tv", "symbol": "AXP", "exchange": "NYSE"},
    "Citigroup":      {"source": "tv", "symbol": "C",     "exchange": "NYSE"},
    "Alibaba":        {"source": "tv", "symbol": "BABA",  "exchange": "NYSE"},
    # Индексы
    "US100":          {"source": "tv", "symbol": "NDX",   "exchange": "NASDAQ"},
    "SP500":          {"source": "tv", "symbol": "SPX",   "exchange": "SP"},
    "DJI30":          {"source": "tv", "symbol": "DJI",   "exchange": "DJ"},
    "DAX":            {"source": "tv", "symbol": "DAX",   "exchange": "XETR"},
    "FTSE 100":       {"source": "tv", "symbol": "UKX",   "exchange": "LSE"},
    "CAC 40":         {"source": "tv", "symbol": "PX1",   "exchange": "EURONEXT"},
    "Nikkei 225":     {"source": "tv", "symbol": "NI225", "exchange": "TVC"},
    "AUS 200":        {"source": "tv", "symbol": "AS51",  "exchange": "TVC"},
    "Euro Stoxx 50":  {"source": "tv", "symbol": "SX5E",  "exchange": "TVC"},
    "Hang Seng":      {"source": "tv", "symbol": "HSI",   "exchange": "TVC"},
    # Товары
    "Gold":           {"source": "tv", "symbol": "GOLD",       "exchange": "TVC"},
    "Silver":         {"source": "tv", "symbol": "SILVER",     "exchange": "TVC"},
    "Oil Brent":      {"source": "tv", "symbol": "UKOIL",      "exchange": "TVC"},
    "Oil WTI":        {"source": "tv", "symbol": "USOIL",      "exchange": "TVC"},
    "Natural Gas":    {"source": "tv", "symbol": "NATURALGAS", "exchange": "TVC"},
    "Platinum":       {"source": "tv", "symbol": "PLATINUM",   "exchange": "TVC"},
}

TV_INTERVAL_MAP = {
    "M1":  {"tv": Interval.in_1_minute,  "binance": "1m"},
    "M3":  {"tv": Interval.in_3_minute,  "binance": "3m"},
    "M5":  {"tv": Interval.in_5_minute,  "binance": "5m"},
    "M10": {"tv": Interval.in_10_minute, "binance": "15m"},
    "M15": {"tv": Interval.in_15_minute, "binance": "15m"},
}

TV_HIGHER_MAP = {
    "M1":  {"tv": Interval.in_5_minute,  "binance": "5m"},
    "M3":  {"tv": Interval.in_15_minute, "binance": "15m"},
    "M5":  {"tv": Interval.in_15_minute, "binance": "15m"},
    "M10": {"tv": Interval.in_1_hour,    "binance": "1h"},
    "M15": {"tv": Interval.in_1_hour,    "binance": "1h"},
}

HISTORY_FILE     = "signals_history.json"
CACHE_TTL        = 30
_cache: dict     = {}

TIMEFRAME_MINUTES = {"M1": 1, "M3": 3, "M5": 5, "M10": 10, "M15": 15}


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


def get_candles_tv(symbol: str, exchange: str, interval: Interval, n_bars: int = 150) -> pd.DataFrame:
    tv = TvDatafeed()
    df = tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=n_bars)
    if df is None or df.empty:
        raise ValueError(f"TvDatafeed вернул пустые данные для {symbol}:{exchange}")
    df = df.reset_index()
    # Rename columns to standard format
    df = df.rename(columns={"datetime": "timestamp"})
    df = df[["timestamp", "open", "high", "low", "close", "volume"]].copy()
    df.dropna(inplace=True)
    return df


def get_candles_binance(ticker: str, timeframe: str, limit: int = 150) -> pd.DataFrame:
    exchange = ccxt.binance({"enableRateLimit": True})
    raw = exchange.fetch_ohlcv(ticker, timeframe, limit=limit)
    df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df


def get_candles(symbol: str, timeframe: str, higher: bool = False) -> pd.DataFrame:
    cache_key = f"{symbol}_{timeframe}_{'h' if higher else 'l'}"
    now = time.time()
    if cache_key in _cache:
        cached_time, cached_df = _cache[cache_key]
        if now - cached_time < CACHE_TTL:
            return cached_df.copy()
    config    = ASSET_CONFIG.get(symbol, {"source": "binance", "ticker": "BTC/USDT"})
    tf_map    = TV_HIGHER_MAP if higher else TV_INTERVAL_MAP
    tf_config = tf_map.get(timeframe, tf_map.get("M1"))
    if config["source"] == "binance":
        df = get_candles_binance(config["ticker"], tf_config["binance"])
    else:
        df = get_candles_tv(config["symbol"], config["exchange"], tf_config["tv"])
    _cache[cache_key] = (now, df.copy())
    return df


def get_current_price(symbol: str) -> float | None:
    try:
        config = ASSET_CONFIG.get(symbol, {"source": "binance", "ticker": "BTC/USDT"})
        if config["source"] == "binance":
            exchange = ccxt.binance({"enableRateLimit": True})
            return exchange.fetch_ticker(config["ticker"])["last"]
        else:
            df = get_candles_tv(config["symbol"], config["exchange"], Interval.in_1_minute, n_bars=1)
            if not df.empty:
                return float(df["close"].iloc[-1])
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

    if (float(last["atr"]) / float(last["close"])) < 0.00005:
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
        "expiry_time": (datetime.now(timezone.utc) + timedelta(minutes=TIMEFRAME_MINUTES.get(payload.timeframe, 1))).isoformat(),
        "win_rate":    calc_win_rate(history),
    }


@app.post("/scan")
def scan_all_timeframes(payload: SignalRequest):
    """AI Сканер — анализирует все таймфреймы сразу."""
    timeframes_to_scan = ["M1", "M3", "M5", "M15"]
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


@app.get("/price")
def get_price(symbol: str):
    return {"symbol": symbol, "price": get_current_price(symbol)}
