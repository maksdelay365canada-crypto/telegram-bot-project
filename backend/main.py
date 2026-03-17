from datetime import datetime, timezone, timedelta
import json
import os
import threading
import time
import logging
import requests as _req
import pandas as pd

logger = logging.getLogger(__name__)
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

# Deriv WebSocket granularity (seconds)
DERIV_GRANULARITY = {"M1": 60, "M3": 180, "M5": 300, "M15": 900}
DERIV_HIGHER_GRAN = {"M1": 300, "M3": 900, "M5": 900, "M15": 3600}

OTC_ASSET_CONFIG = {
    # ── Forex OTC (TradingView real data as proxy) ──────────────────────────
    "EUR/USD OTC": {"source": "tv", "symbol": "EURUSD",  "exchange": "FX", "is_otc": True},
    "GBP/USD OTC": {"source": "tv", "symbol": "GBPUSD",  "exchange": "FX", "is_otc": True},
    "AUD/USD OTC": {"source": "tv", "symbol": "AUDUSD",  "exchange": "FX", "is_otc": True},
    "USD/JPY OTC": {"source": "tv", "symbol": "USDJPY",  "exchange": "FX", "is_otc": True},
    "USD/CAD OTC": {"source": "tv", "symbol": "USDCAD",  "exchange": "FX", "is_otc": True},
    "USD/CHF OTC": {"source": "tv", "symbol": "USDCHF",  "exchange": "FX", "is_otc": True},
    "EUR/GBP OTC": {"source": "tv", "symbol": "EURGBP",  "exchange": "FX", "is_otc": True},
    "EUR/JPY OTC": {"source": "tv", "symbol": "EURJPY",  "exchange": "FX", "is_otc": True},
    "GBP/JPY OTC": {"source": "tv", "symbol": "GBPJPY",  "exchange": "FX", "is_otc": True},
    # ── Deriv Synthetic Indices (24/7, real Deriv data) ─────────────────────
    "Volatility 10":  {"source": "deriv", "symbol": "R_10",      "is_otc": True},
    "Volatility 25":  {"source": "deriv", "symbol": "R_25",      "is_otc": True},
    "Volatility 50":  {"source": "deriv", "symbol": "R_50",      "is_otc": True},
    "Volatility 75":  {"source": "deriv", "symbol": "R_75",      "is_otc": True},
    "Volatility 100": {"source": "deriv", "symbol": "R_100",     "is_otc": True},
    "Boom 500":       {"source": "deriv", "symbol": "BOOM500",   "is_otc": True},
    "Boom 1000":      {"source": "deriv", "symbol": "BOOM1000",  "is_otc": True},
    "Crash 500":      {"source": "deriv", "symbol": "CRASH500",  "is_otc": True},
    "Crash 1000":     {"source": "deriv", "symbol": "CRASH1000", "is_otc": True},
}

ALL_ASSETS = {**ASSET_CONFIG, **OTC_ASSET_CONFIG}

ASSET_CURRENCIES: dict = {
    # Форекс
    "EUR/USD": ["EUR","USD"], "GBP/USD": ["GBP","USD"],
    "AUD/USD": ["AUD","USD"], "USD/JPY": ["USD","JPY"],
    "USD/CAD": ["USD","CAD"], "USD/CHF": ["USD","CHF"],
    "EUR/GBP": ["EUR","GBP"], "EUR/JPY": ["EUR","JPY"],
    "EUR/CHF": ["EUR","CHF"], "EUR/AUD": ["EUR","AUD"],
    "EUR/CAD": ["EUR","CAD"], "GBP/JPY": ["GBP","JPY"],
    "GBP/CHF": ["GBP","CHF"], "GBP/AUD": ["GBP","AUD"],
    "GBP/CAD": ["GBP","CAD"], "AUD/JPY": ["AUD","JPY"],
    "AUD/CAD": ["AUD","CAD"], "AUD/CHF": ["AUD","CHF"],
    "CAD/JPY": ["CAD","JPY"], "CAD/CHF": ["CAD","CHF"],
    "CHF/JPY": ["CHF","JPY"], "NZD/USD": ["NZD","USD"],
    "NZD/JPY": ["NZD","JPY"], "NZD/CAD": ["NZD","CAD"],
    "NZD/CHF": ["NZD","CHF"], "NZD/GBP": ["NZD","GBP"],
    # OTC Форекс (те же валюты)
    "EUR/USD OTC": ["EUR","USD"], "GBP/USD OTC": ["GBP","USD"],
    "AUD/USD OTC": ["AUD","USD"], "USD/JPY OTC": ["USD","JPY"],
    "USD/CAD OTC": ["USD","CAD"], "USD/CHF OTC": ["USD","CHF"],
    "EUR/GBP OTC": ["EUR","GBP"], "EUR/JPY OTC": ["EUR","JPY"],
    "GBP/JPY OTC": ["GBP","JPY"],
    # Крипто (не отслеживаем новости FF)
    "Bitcoin": [], "Ethereum": [], "Dash": [], "Chainlink": [], "Bitcoin Cash": [],
    # Акции → USD
    "Apple": ["USD"], "Microsoft": ["USD"], "Tesla": ["USD"],
    "Netflix": ["USD"], "Amazon": ["USD"], "Google": ["USD"],
    "Meta": ["USD"], "Intel": ["USD"], "Cisco": ["USD"],
    "ExxonMobil": ["USD"], "Johnson & Johnson": ["USD"], "Pfizer": ["USD"],
    "Boeing": ["USD"], "McDonald's": ["USD"], "JPMorgan": ["USD"],
    "American Express": ["USD"], "Citigroup": ["USD"], "Alibaba": ["USD"],
    # Индексы
    "US100": ["USD"], "SP500": ["USD"], "DJI30": ["USD"],
    "DAX": ["EUR"], "FTSE 100": ["GBP"], "CAC 40": ["EUR"],
    "Nikkei 225": ["JPY"], "AUS 200": ["AUD"],
    "Euro Stoxx 50": ["EUR"], "Hang Seng": [],
    # Товары → USD
    "Gold": ["USD"], "Silver": ["USD"], "Oil Brent": ["USD"],
    "Oil WTI": ["USD"], "Natural Gas": ["USD"], "Platinum": ["USD"],
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


class HistoryAddRequest(BaseModel):
    trade_id: str
    signal: str
    confidence: int
    symbol: str
    timeframe: str
    mode_label: str          # "manual" or "ai_scanner"
    is_martingale: bool = False
    martingale_step: int = 0
    entry_price: float | None = None
    expiry_time: str | None = None
    reasons: list[str] = []
    is_otc: bool = False
    market_type: str = "forex"  # "forex" or "otc"


class HistoryUpdateRequest(BaseModel):
    trade_id: str
    result: str              # "WIN" or "LOSS"


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


def get_candles_deriv(symbol: str, granularity: int, count: int = 150) -> pd.DataFrame:
    """Fetch OHLCV candles from Deriv WebSocket API (synthetic indices, 24/7)."""
    import websocket as _ws  # websocket-client, installed via requirements.txt  # noqa: F401
    _WS_URL = "wss://ws.binaryws.com/websockets/v3?app_id=1089"
    collected: list = []
    done_event = threading.Event()

    def on_open(ws):
        ws.send(json.dumps({
            "ticks_history": symbol,
            "end":           "latest",
            "count":         count,
            "granularity":   granularity,
            "style":         "candles",
            "subscribe":     0,
        }))

    def on_message(ws, raw):
        try:
            data = json.loads(raw)
            if data.get("msg_type") == "candles":
                for c in data.get("candles", []):
                    collected.append({
                        "timestamp": datetime.fromtimestamp(c["epoch"], tz=timezone.utc),
                        "open":      float(c["open"]),
                        "high":      float(c["high"]),
                        "low":       float(c["low"]),
                        "close":     float(c["close"]),
                        "volume":    1.0,   # Deriv doesn't provide volume
                    })
                done_event.set()
                try: ws.close()
                except Exception: pass
        except Exception:
            pass

    def on_error(ws, error):
        logger.debug(f"Deriv WS error [{symbol}]: {error}")
        done_event.set()

    def on_close(ws, *args):
        done_event.set()

    ws_app = _ws.WebSocketApp(
        _WS_URL,
        on_open=on_open, on_message=on_message,
        on_error=on_error, on_close=on_close,
    )
    thread = threading.Thread(target=ws_app.run_forever, daemon=True)
    thread.start()
    done_event.wait(timeout=20)
    try: ws_app.close()
    except Exception: pass

    if not collected:
        raise ValueError(f"Deriv: no data received for {symbol}")

    df = pd.DataFrame(collected)
    df.set_index("timestamp", inplace=True)
    df.index = pd.to_datetime(df.index)
    df = df[~df.index.duplicated(keep="last")]
    df.sort_index(inplace=True)
    return df.reset_index()


def get_candles(symbol: str, timeframe: str, higher: bool = False) -> pd.DataFrame:
    cache_key = f"{symbol}_{timeframe}_{'h' if higher else 'l'}"
    now = time.time()
    if cache_key in _cache:
        cached_time, cached_df = _cache[cache_key]
        if now - cached_time < CACHE_TTL:
            return cached_df.copy()

    config    = ALL_ASSETS.get(symbol, {"source": "binance", "ticker": "BTC/USDT"})
    tf_map    = TV_HIGHER_MAP if higher else TV_INTERVAL_MAP
    tf_config = tf_map.get(timeframe, tf_map.get("M1"))

    if config["source"] == "deriv":
        gran_map = DERIV_HIGHER_GRAN if higher else DERIV_GRANULARITY
        df = get_candles_deriv(config["symbol"], gran_map.get(timeframe, 60))
    elif config["source"] == "binance":
        df = get_candles_binance(config["ticker"], tf_config["binance"])
    else:
        df = get_candles_tv(config["symbol"], config["exchange"], tf_config["tv"])

    _cache[cache_key] = (now, df.copy())
    return df


def get_current_price(symbol: str) -> float | None:
    try:
        config = ALL_ASSETS.get(symbol, {"source": "binance", "ticker": "BTC/USDT"})
        if config["source"] == "binance":
            exchange = ccxt.binance({"enableRateLimit": True})
            return exchange.fetch_ticker(config["ticker"])["last"]
        elif config["source"] == "deriv":
            df = get_candles_deriv(config["symbol"], granularity=60, count=2)
            if not df.empty:
                return float(df["close"].iloc[-1])
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
    if len(df) < 3:
        return "none", "neutral"
    c3 = df.iloc[-3]; c2 = df.iloc[-2]; c1 = df.iloc[-1]
    def is_bull(c): return float(c['close']) > float(c['open'])
    def is_bear(c): return float(c['close']) < float(c['open'])
    def body(c): return abs(float(c['close']) - float(c['open']))
    def rng(c):  return float(c['high']) - float(c['low'])
    def usha(c): return float(c['high']) - max(float(c['open']), float(c['close']))
    def lsha(c): return min(float(c['open']), float(c['close'])) - float(c['low'])

    # Doji
    if rng(c1) > 0 and body(c1) / rng(c1) < 0.1:
        return "Doji (неопределённость)", "neutral"
    # Bullish Marubozu
    if is_bull(c1) and rng(c1) > 0 and usha(c1) < body(c1)*0.05 and lsha(c1) < body(c1)*0.05:
        return "Бычье марибозу (сильный рост)", "up"
    # Bearish Marubozu
    if is_bear(c1) and rng(c1) > 0 and usha(c1) < body(c1)*0.05 and lsha(c1) < body(c1)*0.05:
        return "Медвежье марибозу (сильное падение)", "down"
    # Three White Soldiers
    if is_bull(c3) and is_bull(c2) and is_bull(c1):
        if float(c2['close'])>float(c3['close']) and float(c1['close'])>float(c2['close']):
            if float(c2['open'])>float(c3['open']) and float(c1['open'])>float(c2['open']):
                return "Три белых солдата (сильный рост)", "up"
    # Three Black Crows
    if is_bear(c3) and is_bear(c2) and is_bear(c1):
        if float(c2['close'])<float(c3['close']) and float(c1['close'])<float(c2['close']):
            if float(c2['open'])<float(c3['open']) and float(c1['open'])<float(c2['open']):
                return "Три чёрных вороны (сильное падение)", "down"
    # Morning Star
    mid_c3 = (float(c3['open'])+float(c3['close']))/2
    if is_bear(c3) and body(c3)>body(c2)*2 and body(c2)<body(c3)*0.3 and is_bull(c1) and float(c1['close'])>mid_c3:
        return "Утренняя звезда (разворот вверх)", "up"
    # Evening Star
    mid_c3b = (float(c3['open'])+float(c3['close']))/2
    if is_bull(c3) and body(c3)>body(c2)*2 and body(c2)<body(c3)*0.3 and is_bear(c1) and float(c1['close'])<mid_c3b:
        return "Вечерняя звезда (разворот вниз)", "down"
    # Bullish Engulfing
    if is_bear(c2) and is_bull(c1) and float(c1['close'])>float(c2['open']) and float(c1['open'])<float(c2['close']):
        return "Бычье поглощение", "up"
    # Bearish Engulfing
    if is_bull(c2) and is_bear(c1) and float(c1['close'])<float(c2['open']) and float(c1['open'])>float(c2['close']):
        return "Медвежье поглощение", "down"
    # Bullish Harami
    if is_bear(c2) and is_bull(c1) and float(c1['close'])<float(c2['open']) and float(c1['open'])>float(c2['close']):
        return "Бычье харами (разворот вверх)", "up"
    # Bearish Harami
    if is_bull(c2) and is_bear(c1) and float(c1['close'])>float(c2['open']) and float(c1['open'])<float(c2['close']):
        return "Медвежье харами (разворот вниз)", "down"
    # Piercing Line
    mid_c2 = (float(c2['open'])+float(c2['close']))/2
    if is_bear(c2) and is_bull(c1) and float(c1['open'])<float(c2['close']) and float(c1['close'])>mid_c2:
        return "Пронизывающая линия (бычий разворот)", "up"
    # Dark Cloud Cover
    mid_c2b = (float(c2['open'])+float(c2['close']))/2
    if is_bull(c2) and is_bear(c1) and float(c1['open'])>float(c2['close']) and float(c1['close'])<mid_c2b:
        return "Завеса из тёмных облаков (медвежий разворот)", "down"
    # Hammer
    if lsha(c1) > body(c1)*2 and usha(c1) < body(c1)*0.5:
        if is_bear(c2) or is_bear(c3):
            return "Молот (разворот вверх)", "up"
    # Hanging Man
    if lsha(c1) > body(c1)*2 and usha(c1) < body(c1)*0.5:
        if is_bull(c2) and is_bull(c3):
            return "Повешенный (разворот вниз)", "down"
    # Inverted Hammer
    if usha(c1) > body(c1)*2 and lsha(c1) < body(c1)*0.5 and is_bull(c1):
        return "Перевёрнутый молот (разворот вверх)", "up"
    # Shooting Star
    if usha(c1) > body(c1)*2 and lsha(c1) < body(c1)*0.5 and is_bear(c1):
        return "Падающая звезда (разворот вниз)", "down"
    return "none", "neutral"


def find_support_resistance(df: pd.DataFrame, window: int = 15) -> dict:
    """Find key support/resistance levels using local extremes + clustering."""
    if len(df) < window * 2 + 1:
        return {"support_levels": [], "resistance_levels": [],
                "nearest_support": None, "nearest_resistance": None,
                "distance_to_support_pct": None, "distance_to_resistance_pct": None}
    resistances, supports = [], []
    for i in range(window, len(df) - window):
        hi = float(df['high'].iloc[i])
        lo = float(df['low'].iloc[i])
        if hi == float(df['high'].iloc[i-window:i+window].max()):
            resistances.append(hi)
        if lo == float(df['low'].iloc[i-window:i+window].min()):
            supports.append(lo)

    def cluster(lvls):
        if not lvls: return []
        lvls = sorted(lvls)
        clusters, cur = [], [lvls[0]]
        for v in lvls[1:]:
            if cur and abs(v - cur[-1]) / max(cur[-1], 1e-10) < 0.001:
                cur.append(v)
            else:
                clusters.append(round(sum(cur)/len(cur), 5)); cur = [v]
        clusters.append(round(sum(cur)/len(cur), 5))
        return clusters

    current = float(df['close'].iloc[-1])
    res_cl  = cluster(resistances)
    sup_cl  = cluster(supports)
    above   = sorted([r for r in res_cl if r > current])[:3]
    below   = sorted([s for s in sup_cl if s < current], reverse=True)[:3]
    nearest_r = above[0] if above else None
    nearest_s = below[0] if below else None
    return {
        "resistance_levels": above,
        "support_levels":    below,
        "nearest_resistance": nearest_r,
        "nearest_support":    nearest_s,
        "distance_to_resistance_pct": round((nearest_r - current)/current*100, 3) if nearest_r else None,
        "distance_to_support_pct":    round((current - nearest_s)/current*100, 3) if nearest_s else None,
    }


def detect_chart_patterns(df: pd.DataFrame) -> dict:
    """Detect classical TA chart patterns."""
    null_result = {"pattern_name": None, "pattern_type": "neutral", "confidence": 0,
                   "description": "", "target_price": None}
    if len(df) < 30:
        return null_result

    h = df['high'].values.astype(float)
    l = df['low'].values.astype(float)
    c = df['close'].values.astype(float)
    n = min(50, len(df))
    h, l, c = h[-n:], l[-n:], c[-n:]
    current = c[-1]

    def peaks(arr, w=5):
        return [(i, float(arr[i])) for i in range(w, len(arr)-w)
                if arr[i] == arr[i-w:i+w+1].max()]
    def troughs(arr, w=5):
        return [(i, float(arr[i])) for i in range(w, len(arr)-w)
                if arr[i] == arr[i-w:i+w+1].min()]

    pks = peaks(h); trs = troughs(l)

    # Double Top
    if len(pks) >= 2:
        p1, p2 = pks[-2], pks[-1]
        if abs(p1[1]-p2[1])/max(p1[1],1e-10) < 0.003 and p2[0] > p1[0]:
            neck = float(min(l[p1[0]:p2[0]+1])) if p2[0] > p1[0] else l[p1[0]]
            return {"pattern_name": "Двойная вершина", "pattern_type": "bearish",
                    "confidence": 72, "description": "Два пика на одном уровне — разворот вниз",
                    "target_price": round(neck-(p1[1]-neck), 5)}
    # Double Bottom
    if len(trs) >= 2:
        t1, t2 = trs[-2], trs[-1]
        if abs(t1[1]-t2[1])/max(t1[1],1e-10) < 0.003 and t2[0] > t1[0]:
            neck = float(max(h[t1[0]:t2[0]+1])) if t2[0] > t1[0] else h[t1[0]]
            return {"pattern_name": "Двойное дно", "pattern_type": "bullish",
                    "confidence": 72, "description": "Два дна на одном уровне — разворот вверх",
                    "target_price": round(neck+(neck-t1[1]), 5)}
    # H&S
    if len(pks) >= 3:
        p1, p2, p3 = pks[-3], pks[-2], pks[-1]
        if p2[1]>p1[1] and p2[1]>p3[1] and abs(p1[1]-p3[1])/max(p2[1],1e-10) < 0.02:
            neck = float(min(l[p1[0]:p3[0]+1])) if p3[0] > p1[0] else l[p1[0]]
            return {"pattern_name": "Голова и плечи", "pattern_type": "bearish",
                    "confidence": 78, "description": "Центральный пик выше боковых — медвежий разворот",
                    "target_price": round(neck-(p2[1]-neck), 5)}
    # Inverse H&S
    if len(trs) >= 3:
        t1, t2, t3 = trs[-3], trs[-2], trs[-1]
        if t2[1]<t1[1] and t2[1]<t3[1] and abs(t1[1]-t3[1])/max(abs(t2[1]),1e-10) < 0.02:
            neck = float(max(h[t1[0]:t3[0]+1])) if t3[0] > t1[0] else h[t1[0]]
            return {"pattern_name": "Обратные голова и плечи", "pattern_type": "bullish",
                    "confidence": 78, "description": "Центральное дно ниже боковых — бычий разворот",
                    "target_price": round(neck+(neck-t2[1]), 5)}
    # Ascending Triangle
    if len(pks) >= 2 and len(trs) >= 2:
        if abs(pks[-1][1]-pks[-2][1])/max(pks[-1][1],1e-10) < 0.005 and trs[-1][1] > trs[-2][1]:
            return {"pattern_name": "Восходящий треугольник", "pattern_type": "bullish",
                    "confidence": 65, "description": "Горизонтальное сопротивление + растущая поддержка — пробой вверх",
                    "target_price": round(float(pks[-1][1]), 5)}
        if abs(trs[-1][1]-trs[-2][1])/max(trs[-1][1],1e-10) < 0.005 and pks[-1][1] < pks[-2][1]:
            return {"pattern_name": "Нисходящий треугольник", "pattern_type": "bearish",
                    "confidence": 65, "description": "Горизонтальная поддержка + падающее сопротивление — пробой вниз",
                    "target_price": round(float(trs[-1][1]), 5)}
    # Flag
    if len(c) >= 30:
        prior_move  = c[-10] - c[-30]
        recent_rng  = (max(h[-10:]) - min(l[-10:])) / max(current, 1e-10)
        prior_rng   = (max(h[-30:-10]) - min(l[-30:-10])) / max(current, 1e-10)
        if prior_rng > 0.005 and recent_rng < prior_rng * 0.4:
            if prior_move > 0:
                return {"pattern_name": "Бычий флаг", "pattern_type": "bullish",
                        "confidence": 60, "description": "Консолидация после роста — продолжение вверх",
                        "target_price": round(current+abs(prior_move), 5)}
            else:
                return {"pattern_name": "Медвежий флаг", "pattern_type": "bearish",
                        "confidence": 60, "description": "Консолидация после падения — продолжение вниз",
                        "target_price": round(current-abs(prior_move), 5)}
    return null_result


def analyze_trend_strength(df: pd.DataFrame) -> dict:
    """Analyze trend direction and strength using ADX."""
    df2 = df.copy()
    try:
        adx_result = ta.adx(df2['high'], df2['low'], df2['close'], length=14)
        adx_col = [c for c in adx_result.columns if c.startswith('ADX_')]
        adx_val = float(adx_result[adx_col[0]].iloc[-1]) if adx_col else 0.0
        if pd.isna(adx_val): adx_val = 0.0
    except Exception:
        adx_val = 0.0

    ema9  = ta.ema(df2['close'], length=9)
    ema21 = ta.ema(df2['close'], length=21)
    direction = "sideways"
    if not ema9.empty and not ema21.empty:
        if float(ema9.iloc[-1]) > float(ema21.iloc[-1]):   direction = "up"
        elif float(ema9.iloc[-1]) < float(ema21.iloc[-1]): direction = "down"

    closes = df2['close'].values.astype(float)
    bars_in_trend = 1
    if direction == "up":
        for i in range(len(closes)-2, max(len(closes)-30,0), -1):
            if closes[i] < closes[i-1]: break
            bars_in_trend += 1
    elif direction == "down":
        for i in range(len(closes)-2, max(len(closes)-30,0), -1):
            if closes[i] > closes[i-1]: break
            bars_in_trend += 1

    if adx_val > 40:   strength = "strong"
    elif adx_val > 20: strength = "moderate"
    else:              strength, direction = "weak", "sideways"

    return {"direction": direction, "strength": strength,
            "adx_value": round(adx_val, 1), "bars_in_trend": bars_in_trend}


def calculate_fibonacci(df: pd.DataFrame) -> dict:
    """Calculate Fibonacci retracement levels from last 50-bar swing."""
    null_result = {"fib_236": None, "fib_382": None, "fib_500": None,
                   "fib_618": None, "fib_786": None,
                   "nearest_level_name": None, "nearest_level_price": None, "all_levels": {}}
    if len(df) < 20: return null_result
    n = min(50, len(df))
    swing_high = float(df['high'].iloc[-n:].max())
    swing_low  = float(df['low'].iloc[-n:].min())
    diff = swing_high - swing_low
    if diff < 1e-10: return null_result
    current = float(df['close'].iloc[-1])
    levels = {
        "0%":    round(swing_high, 5),
        "23.6%": round(swing_high - diff*0.236, 5),
        "38.2%": round(swing_high - diff*0.382, 5),
        "50%":   round(swing_high - diff*0.500, 5),
        "61.8%": round(swing_high - diff*0.618, 5),
        "78.6%": round(swing_high - diff*0.786, 5),
        "100%":  round(swing_low, 5),
    }
    nearest_name  = min(levels, key=lambda k: abs(levels[k]-current))
    nearest_price = levels[nearest_name]
    return {"fib_236": levels["23.6%"], "fib_382": levels["38.2%"],
            "fib_500": levels["50%"],   "fib_618": levels["61.8%"],
            "fib_786": levels["78.6%"],
            "nearest_level_name": nearest_name, "nearest_level_price": nearest_price,
            "all_levels": levels}


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
def get_history(limit: int = 20, offset: int = 0,
                mode: str | None = None, result: str | None = None,
                symbol: str | None = None):
    history = load_history()
    history = [e for e in history if e.get("trade_id")]

    # Filters
    if mode:   history = [e for e in history if e.get("mode") == mode]
    if result: history = [e for e in history if e.get("result") == result]
    if symbol: history = [e for e in history if e.get("symbol") == symbol]

    total = len(history)
    finished  = [e for e in history if e.get("result") in ("WIN","LOSS")]
    manual_f  = [e for e in finished if e.get("mode") == "manual"]
    ai_f      = [e for e in finished if e.get("mode") == "ai_scanner"]

    def wr(lst):
        if not lst: return 0.0
        wins = sum(1 for e in lst if e["result"] == "WIN")
        return round(wins/len(lst)*100, 1)

    streak, streak_type = 0, None
    for e in reversed(finished):
        if streak_type is None: streak_type = e["result"]; streak = 1
        elif e["result"] == streak_type: streak += 1
        else: break

    page = list(reversed(history))[offset:offset+limit]
    return {
        "history":  page,
        "total":    total,
        "win_rate": wr(finished),
        "stats": {
            "win_rate":        wr(finished),
            "win_rate_manual": wr(manual_f),
            "win_rate_ai":     wr(ai_f),
            "total":           total,
            "wins":            sum(1 for e in finished if e["result"] == "WIN"),
            "losses":          sum(1 for e in finished if e["result"] == "LOSS"),
            "pending":         sum(1 for e in history if e.get("result") == "PENDING"),
            "streak":          streak,
            "streak_type":     streak_type,
        },
    }


@app.post("/history/add")
def add_history_entry(payload: HistoryAddRequest):
    history = load_history()
    history.append({
        "trade_id":        payload.trade_id,
        "signal":          payload.signal,
        "confidence":      payload.confidence,
        "symbol":          payload.symbol,
        "timeframe":       payload.timeframe,
        "mode":            payload.mode_label,
        "is_martingale":   payload.is_martingale,
        "martingale_step": payload.martingale_step,
        "entry_confirmed": True,
        "entry_price":     payload.entry_price,
        "result":          "PENDING",
        "result_confirmed": False,
        "expiry_time":     payload.expiry_time,
        "reasons":         payload.reasons,
        "is_otc":          payload.is_otc,
        "market_type":     payload.market_type,
        "timestamp":       datetime.now(timezone.utc).isoformat(),
    })
    save_history(history)
    return {"ok": True}


@app.post("/history/update")
def update_history_entry(payload: HistoryUpdateRequest):
    history = load_history()
    for entry in reversed(history):
        if entry.get("trade_id") == payload.trade_id:
            entry["result"] = payload.result
            entry["result_confirmed"] = True
            break
    save_history(history)
    return {"ok": True}


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

    now = datetime.now(timezone.utc)
    history = load_history()

    asset_cfg = ALL_ASSETS.get(payload.symbol, {})
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
        "timestamp":   now.isoformat(),
        "expiry_time": (now + timedelta(minutes=TIMEFRAME_MINUTES.get(payload.timeframe, 1))).isoformat(),
        "win_rate":    calc_win_rate(history),
        "is_otc":      asset_cfg.get("is_otc", False),
        "market_type": "otc" if asset_cfg.get("is_otc") else "forex",
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
                "timeframe":   tf,
                "signal":      result["signal"],
                "confidence":  result["confidence"],
                "reasons":     result["reasons"],
                "state":       result["state"],
                "entry_price": result.get("entry_price"),
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


@app.post("/signal/details")
def get_signal_details(payload: SignalRequest):
    """Detailed technical analysis — runs after fast /signal."""
    try:
        df = get_candles(payload.symbol, payload.timeframe, higher=False)
        sr          = find_support_resistance(df)
        fib         = calculate_fibonacci(df)
        trend       = analyze_trend_strength(df)
        chart_pat   = detect_chart_patterns(df)
        current     = float(df['close'].iloc[-1]) if not df.empty else None
        risk_level  = "средний"
        if sr.get('distance_to_support_pct') is not None:
            d = sr['distance_to_support_pct']
            risk_level = "низкий" if d < 0.3 else "высокий" if d > 0.7 else "средний"
        entry_rec = None
        if current:
            entry_rec = {
                "optimal_entry": current,
                "entry_zone":    f"{round(current*0.9999,5)} — {round(current*1.0001,5)}",
                "stop_zone":     f"ниже {sr['nearest_support']}" if sr.get('nearest_support') else "—",
                "risk_level":    risk_level,
            }
        return {
            "symbol":              payload.symbol,
            "timeframe":           payload.timeframe,
            "support_resistance":  sr,
            "fibonacci":           fib,
            "trend":               trend,
            "chart_pattern":       chart_pat,
            "entry_recommendation": entry_rec,
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/history/stats")
def get_history_stats():
    history = load_history()
    history = [e for e in history if e.get("trade_id")]
    finished = [e for e in history if e.get("result") in ("WIN","LOSS")]

    def wr(lst):
        if not lst: return 0.0
        return round(sum(1 for e in lst if e["result"]=="WIN")/len(lst)*100, 1)

    # Best/worst symbol
    from collections import defaultdict
    sym_stats = defaultdict(lambda: {"w":0,"l":0})
    for e in finished:
        sym = e.get("symbol","?")
        if e["result"] == "WIN": sym_stats[sym]["w"] += 1
        else:                    sym_stats[sym]["l"] += 1
    best_sym  = max(sym_stats, key=lambda s: sym_stats[s]["w"]/(sym_stats[s]["w"]+sym_stats[s]["l"]), default=None)
    worst_sym = min(sym_stats, key=lambda s: sym_stats[s]["w"]/(sym_stats[s]["w"]+sym_stats[s]["l"]), default=None)

    # Streaks
    cur_streak, cur_type = 0, None
    for e in reversed(finished):
        if cur_type is None: cur_type = e["result"]; cur_streak = 1
        elif e["result"] == cur_type: cur_streak += 1
        else: break

    max_win_streak = max_loss_streak = 0
    cur_w = cur_l = 0
    for e in finished:
        if e["result"]=="WIN":  cur_w += 1; cur_l = 0
        else:                   cur_l += 1; cur_w = 0
        max_win_streak  = max(max_win_streak,  cur_w)
        max_loss_streak = max(max_loss_streak, cur_l)

    return {
        "total_trades":        len(history),
        "total_wins":          sum(1 for e in finished if e["result"]=="WIN"),
        "total_losses":        sum(1 for e in finished if e["result"]=="LOSS"),
        "total_pending":       sum(1 for e in history if e.get("result")=="PENDING"),
        "win_rate_overall":    wr(finished),
        "win_rate_manual":     wr([e for e in finished if e.get("mode")=="manual"]),
        "win_rate_ai_scanner": wr([e for e in finished if e.get("mode")=="ai_scanner"]),
        "best_symbol":         best_sym,
        "worst_symbol":        worst_sym,
        "current_streak":      cur_streak,
        "current_streak_type": cur_type,
        "longest_win_streak":  max_win_streak,
        "longest_loss_streak": max_loss_streak,
    }


# ── Sessions ──────────────────────────────────────────────────────────────────
import uuid as _uuid

SESSIONS_FILE = "sessions.json"

class SessionStartRequest(BaseModel):
    deposit: float
    risk_pct: float = 5.0
    max_martingale: int = 3

class SessionEndRequest(BaseModel):
    session_id: str

def load_sessions() -> list:
    if not os.path.exists(SESSIONS_FILE): return []
    with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
        try: return json.load(f)
        except: return []

def save_sessions(sessions: list):
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)

@app.post("/session/start")
def start_session(payload: SessionStartRequest):
    sessions = load_sessions()
    # End any currently active session
    for s in sessions:
        if s.get("ended_at") is None:
            s["ended_at"] = datetime.now(timezone.utc).isoformat()
            s["end_reason"] = "auto_closed"
    session_id = str(_uuid.uuid4())
    sessions.append({
        "id":            session_id,
        "started_at":    datetime.now(timezone.utc).isoformat(),
        "ended_at":      None,
        "deposit":       payload.deposit,
        "risk_pct":      payload.risk_pct,
        "max_martingale": payload.max_martingale,
        "trade_ids":     [],
        "wins":          0,
        "losses":        0,
        "pnl":           0.0,
        "end_reason":    None,
    })
    save_sessions(sessions)
    return {"session_id": session_id, "started_at": sessions[-1]["started_at"]}

@app.post("/session/end")
def end_session(payload: SessionEndRequest):
    sessions = load_sessions()
    for s in sessions:
        if s["id"] == payload.session_id and s.get("ended_at") is None:
            s["ended_at"]  = datetime.now(timezone.utc).isoformat()
            s["end_reason"] = "manual"
            save_sessions(sessions)
            return s
    return {"error": "session not found or already ended"}

@app.get("/session/current")
def get_current_session():
    sessions = load_sessions()
    for s in reversed(sessions):
        if s.get("ended_at") is None:
            # Attach trade details
            history = load_history()
            trades  = [e for e in history if e.get("trade_id") in s.get("trade_ids", [])]
            s["trades_detail"] = trades
            return s
    return {"active": False}

@app.get("/session/history")
def get_session_history():
    sessions = load_sessions()
    return {"sessions": list(reversed(sessions[-20:]))}

@app.get("/session/{session_id}")
def get_session(session_id: str):
    sessions = load_sessions()
    for s in sessions:
        if s["id"] == session_id:
            history = load_history()
            trades  = [e for e in history if e.get("trade_id") in s.get("trade_ids", [])]
            s["trades_detail"] = trades
            return s
    return {"error": "not found"}

@app.post("/session/add_trade")
def add_trade_to_session(payload: dict):
    """Called when user confirms a trade — links it to active session."""
    trade_id   = payload.get("trade_id")
    result     = payload.get("result")       # "WIN" | "LOSS" | None
    trade_size = payload.get("trade_size", 0)
    pnl_delta  = payload.get("pnl_delta", 0)
    sessions = load_sessions()
    for s in reversed(sessions):
        if s.get("ended_at") is None:
            if trade_id and trade_id not in s.get("trade_ids", []):
                s.setdefault("trade_ids", []).append(trade_id)
            if result == "WIN":
                s["wins"]  = s.get("wins", 0)  + 1
                s["pnl"]   = s.get("pnl",  0)  + abs(pnl_delta)
            elif result == "LOSS":
                s["losses"] = s.get("losses", 0) + 1
                s["pnl"]    = s.get("pnl",  0)  - abs(pnl_delta)
            # Auto-stop: 3 losses in a row or >20% drawdown
            recent = s.get("trade_ids", [])
            history = load_history()
            recent_results = [e.get("result") for e in history
                              if e.get("trade_id") in recent[-3:]]
            if recent_results.count("LOSS") >= 3:
                s["ended_at"]  = datetime.now(timezone.utc).isoformat()
                s["end_reason"] = "martingale_limit"
            save_sessions(sessions)
            return {"ok": True, "session": s}
    return {"ok": False, "reason": "no active session"}


# ── News Calendar ─────────────────────────────────────────────────────────────

_news_cache: dict = {"data": None, "ts": 0.0}
_NEWS_TTL = 300  # 5 minutes


def _fetch_news_raw() -> list:
    now = time.time()
    if _news_cache["data"] is not None and now - _news_cache["ts"] < _NEWS_TTL:
        return _news_cache["data"]
    try:
        resp = _req.get(
            "https://nfs.faireconomy.media/ff_calendar_thisweek.json",
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        data = resp.json()
        _news_cache["data"] = data
        _news_cache["ts"] = now
        return data
    except Exception as e:
        logger.warning(f"News fetch error: {e}")
        return _news_cache["data"] or []


def _parse_ff_time(date_str: str, time_str: str) -> datetime | None:
    if not time_str or time_str.lower() in ("tentative", "all day", ""):
        return None
    try:
        date_part = None
        for fmt in ("%Y-%m-%d", "%b %d, %Y"):
            try:
                date_part = datetime.strptime(date_str.strip(), fmt)
                break
            except ValueError:
                continue
        if date_part is None:
            return None

        time_str_c = time_str.strip().lower()
        time_part = None
        for tfmt in ("%I:%M%p", "%H:%M", "%I%p"):
            try:
                time_part = datetime.strptime(time_str_c, tfmt)
                break
            except ValueError:
                continue
        if time_part is None:
            return None

        dt = date_part.replace(
            hour=time_part.hour, minute=time_part.minute, second=0,
            tzinfo=timezone(timedelta(hours=-5)),  # Eastern Time
        )
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def _build_news_event(ev: dict, now: datetime) -> dict:
    ev_time = _parse_ff_time(ev.get("date", ""), ev.get("time", ""))
    impact = ev.get("impact", "Low").lower()
    if impact not in ("high", "medium", "low"):
        impact = "low"
    minutes_until = None
    if ev_time:
        minutes_until = int((ev_time - now).total_seconds() / 60)
    return {
        "time_utc":      ev_time.isoformat() if ev_time else None,
        "currency":      ev.get("country", ""),
        "title":         ev.get("title", ""),
        "impact":        impact,
        "forecast":      ev.get("forecast") or "",
        "previous":      ev.get("previous") or "",
        "actual":        ev.get("actual") or None,
        "minutes_until": minutes_until,
    }


@app.get("/news")
def get_news(currency: str | None = None):
    raw = _fetch_news_raw()
    now = datetime.now(timezone.utc)
    events = [_build_news_event(ev, now) for ev in raw]

    if currency:
        currencies = {c.strip().upper() for c in currency.split(",")}
        events = [e for e in events if e["currency"].upper() in currencies]

    events.sort(key=lambda e: e["minutes_until"] if e["minutes_until"] is not None else 999999)

    upcoming_imp = [
        e for e in events
        if e["impact"] in ("high", "medium")
        and e["minutes_until"] is not None
        and 0 <= e["minutes_until"] <= 30
    ]
    warning = bool(upcoming_imp)
    warning_message = None
    if upcoming_imp:
        e = upcoming_imp[0]
        warning_message = (
            f"Важная новость через {e['minutes_until']} мин: "
            f"{e['currency']} — {e['title']}"
        )

    return {"events": events, "warning": warning, "warning_message": warning_message}


@app.get("/news/check")
def check_news_for_symbol(symbol: str):
    currencies = ASSET_CURRENCIES.get(symbol, [])
    if not currencies:
        return {"warning": False, "warning_message": None, "events": []}

    raw = _fetch_news_raw()
    now = datetime.now(timezone.utc)

    relevant = []
    for ev in raw:
        if ev.get("country", "").upper() not in [c.upper() for c in currencies]:
            continue
        impact = ev.get("impact", "Low").lower()
        if impact not in ("high", "medium"):
            continue
        ev_time = _parse_ff_time(ev.get("date", ""), ev.get("time", ""))
        if not ev_time:
            continue
        minutes_until = int((ev_time - now).total_seconds() / 60)
        if -5 <= minutes_until <= 30:
            relevant.append({
                "currency":      ev.get("country", ""),
                "title":         ev.get("title", ""),
                "impact":        impact,
                "minutes_until": minutes_until,
            })

    warning = bool(relevant)
    warning_message = None
    if relevant:
        e = relevant[0]
        m = e["minutes_until"]
        icon = "🔴" if e["impact"] == "high" else "🟡"
        if m >= 0:
            warning_message = (
                f"Через {m} мин выходит важная новость:\n"
                f"{icon} {e['currency']} — {e['title']}"
            )
        else:
            warning_message = (
                f"Только что вышла новость:\n"
                f"{icon} {e['currency']} — {e['title']}\n"
                f"Возможна повышенная волатильность"
            )

    return {"warning": warning, "warning_message": warning_message, "events": relevant}
