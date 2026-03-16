"""
Minimal TvDatafeed implementation — vendored for Railway deployment.
Based on the open-source StreamAlpha/tvdatafeed library (MIT License).
"""
import json
import logging
import random
import re
import string
from datetime import datetime
from enum import Enum

import pandas as pd
import websocket

logger = logging.getLogger(__name__)

# TradingView WebSocket URL
_WS_URL = "wss://data.tradingview.com/socket.io/websocket?from=chart%2F"


class Interval(Enum):
    in_1_minute  = "1"
    in_3_minute  = "3"
    in_5_minute  = "5"
    in_10_minute = "10"
    in_15_minute = "15"
    in_30_minute = "30"
    in_45_minute = "45"
    in_1_hour    = "60"
    in_2_hour    = "120"
    in_3_hour    = "180"
    in_4_hour    = "240"
    in_daily     = "1D"
    in_weekly    = "1W"
    in_monthly   = "1M"


def _rand_str(n: int = 12) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=n))


def _frame(msg: str) -> str:
    return f"~m~{len(msg)}~m~{msg}"


def _msg(func: str, params: list) -> str:
    return _frame(json.dumps({"m": func, "p": params}, separators=(",", ":")))


class TvDatafeed:
    def __init__(self, username: str = None, password: str = None):
        self._token = "unauthorized_user_token"
        # Auth is optional — anonymous access works for most public symbols
        if username and password:
            try:
                self._token = self._get_token(username, password)
            except Exception as e:
                logger.warning(f"TvDatafeed auth failed: {e}. Using anonymous token.")

    @staticmethod
    def _get_token(username: str, password: str) -> str:
        import requests
        r = requests.post(
            "https://www.tradingview.com/accounts/signin/",
            data={"username": username, "password": password, "remember": "on"},
            headers={"Referer": "https://www.tradingview.com"},
            timeout=10,
        )
        data = r.json()
        return data["user"]["auth_token"]

    def get_hist(
        self,
        symbol: str,
        exchange: str,
        interval: Interval,
        n_bars: int = 300,
    ) -> pd.DataFrame:
        """
        Fetch OHLCV history from TradingView.
        Returns DataFrame with index=datetime, columns=[open,high,low,close,volume].
        Returns empty DataFrame on failure.
        """
        full_symbol = f"{exchange}:{symbol}"
        iv = interval.value if isinstance(interval, Interval) else str(interval)

        chart_sess = f"cs_{_rand_str(12)}"
        quote_sess = f"qs_{_rand_str(12)}"

        collected: list[dict] = []
        done = False

        def on_open(ws):
            ws.send(_msg("set_auth_token",   [self._token]))
            ws.send(_msg("chart_create_session", [chart_sess, ""]))
            ws.send(_msg("quote_create_session", [quote_sess]))
            ws.send(_msg("quote_add_symbols",
                         [quote_sess, full_symbol, {"flags": ["force_permission"]}]))
            ws.send(_msg("resolve_symbol",
                         [chart_sess, "sym_1",
                          f'={{"symbol":"{full_symbol}","adjustment":"splits"}}'
                          ]))
            ws.send(_msg("create_series",
                         [chart_sess, "s1", "s1", "sym_1", iv, n_bars]))

        def on_message(ws, raw):
            nonlocal done
            # Heartbeat
            if "~h~" in raw:
                for part in raw.split("~m~"):
                    if part.startswith("~h~"):
                        ws.send(_frame(part))
                return

            for chunk in re.split(r"~m~\d+~m~", raw):
                if not chunk:
                    continue
                try:
                    obj = json.loads(chunk)
                except json.JSONDecodeError:
                    continue

                m_type = obj.get("m", "")
                if m_type not in ("timescale_update", "du"):
                    continue

                payload = obj.get("p", [None, {}])
                series_data = payload[1] if len(payload) > 1 else {}
                s1 = series_data.get("s1")
                if not s1:
                    continue

                for bar in s1.get("s", []):
                    v = bar.get("v", [])
                    if len(v) < 5:
                        continue
                    collected.append({
                        "datetime": datetime.utcfromtimestamp(v[0]),
                        "open":     v[1],
                        "high":     v[2],
                        "low":      v[3],
                        "close":    v[4],
                        "volume":   v[5] if len(v) > 5 else 0.0,
                    })

                if collected:
                    done = True
                    ws.close()

        def on_error(ws, error):
            logger.error(f"TvDatafeed WS error for {full_symbol}: {error}")
            ws.close()

        ws = websocket.WebSocketApp(
            _WS_URL,
            header={"Origin": "https://data.tradingview.com"},
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
        )
        ws.run_forever(ping_interval=20, ping_timeout=10)

        if not collected:
            logger.warning(f"TvDatafeed: no data for {full_symbol} {iv}")
            return pd.DataFrame()

        df = pd.DataFrame(collected)
        df.set_index("datetime", inplace=True)
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        return df
