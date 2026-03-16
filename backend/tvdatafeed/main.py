"""
Minimal TvDatafeed implementation — vendored for Railway deployment.
Based on the open-source StreamAlpha/tvdatafeed library (MIT License).
"""
import json
import logging
import random
import re
import string
import threading
from datetime import datetime
from enum import Enum

import pandas as pd
import websocket

logger = logging.getLogger(__name__)

_WS_URL = "wss://data.tradingview.com/socket.io/websocket?from=chart%2F"
_TIMEOUT = 20  # max seconds to wait for data


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
        return r.json()["user"]["auth_token"]

    def get_hist(
        self,
        symbol: str,
        exchange: str,
        interval: Interval,
        n_bars: int = 300,
    ) -> pd.DataFrame:
        full_symbol = f"{exchange}:{symbol}"
        iv = interval.value if isinstance(interval, Interval) else str(interval)

        chart_sess = f"cs_{_rand_str(12)}"
        quote_sess = f"qs_{_rand_str(12)}"

        collected: list = []
        done_event = threading.Event()
        ws_ref: list = [None]

        def on_open(ws):
            ws_ref[0] = ws
            ws.send(_msg("set_auth_token",       [self._token]))
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
            # Heartbeat
            for part in re.split(r"~m~\d+~m~", raw):
                if part.startswith("~h~"):
                    try:
                        ws.send(_frame(part))
                    except Exception:
                        pass

            # Parse JSON chunks
            for chunk in re.split(r"~m~\d+~m~", raw):
                if not chunk or not chunk.startswith("{"):
                    continue
                try:
                    obj = json.loads(chunk)
                except json.JSONDecodeError:
                    continue

                m_type = obj.get("m", "")
                if m_type not in ("timescale_update", "du"):
                    continue

                payload = obj.get("p", [])
                series_map = payload[1] if len(payload) > 1 else {}
                s1 = series_map.get("s1") if isinstance(series_map, dict) else None
                if not s1:
                    continue

                bars = s1.get("s", [])
                for bar in bars:
                    v = bar.get("v", [])
                    if len(v) < 5:
                        continue
                    collected.append({
                        "datetime": datetime.utcfromtimestamp(v[0]),
                        "open":     float(v[1]),
                        "high":     float(v[2]),
                        "low":      float(v[3]),
                        "close":    float(v[4]),
                        "volume":   float(v[5]) if len(v) > 5 else 0.0,
                    })

                if collected:
                    done_event.set()
                    try:
                        ws.close()
                    except Exception:
                        pass

        def on_error(ws, error):
            logger.debug(f"TvDatafeed WS error [{full_symbol}]: {error}")
            done_event.set()

        def on_close(ws, *args):
            done_event.set()

        ws = websocket.WebSocketApp(
            _WS_URL,
            header={"Origin": "https://data.tradingview.com"},
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
        )

        thread = threading.Thread(
            target=ws.run_forever,
            kwargs={"ping_interval": 10, "ping_timeout": 5},
            daemon=True,
        )
        thread.start()

        # Wait at most _TIMEOUT seconds
        done_event.wait(timeout=_TIMEOUT)
        try:
            ws.close()
        except Exception:
            pass

        if not collected:
            logger.warning(f"TvDatafeed: no data received for {full_symbol} interval={iv}")
            return pd.DataFrame()

        df = pd.DataFrame(collected)
        df.set_index("datetime", inplace=True)
        df.index = pd.to_datetime(df.index)
        df = df[~df.index.duplicated(keep="last")]
        df.sort_index(inplace=True)
        return df
