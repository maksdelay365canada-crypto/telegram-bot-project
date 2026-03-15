import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import httpx

# ── Настройки ──
BOT_TOKEN = "7796005388:AAGu2HYvBRujBIfu4K2DzTxgr3ZFlHW3D80"
CHAT_ID   = 884778391
BACKEND   = "http://127.0.0.1:8000"
MINI_APP_URL = "https://sunny-piroshki-176919.netlify.app"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_state = {
    "symbol":   "Bitcoin OTC",
    "mode":     "Уверенный",
}

SYMBOLS = [
    "Bitcoin OTC", "Ethereum OTC", "Solana OTC", "BNB OTC",
    "EUR/USD OTC", "GBP/USD OTC", "Gold OTC", "Brent Oil OTC",
    "Tesla OTC", "Apple OTC", "Amazon OTC",
]


def main_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🚀 Открыть Mini App",
                web_app=WebAppInfo(url=MINI_APP_URL)
            ),
        ],
        [
            InlineKeyboardButton("📊 Сигнал M1", callback_data="signal_M1"),
            InlineKeyboardButton("📊 Сигнал M5", callback_data="signal_M5"),
        ],
        [
            InlineKeyboardButton("🤖 AI Сканер", callback_data="scan"),
        ],
        [
            InlineKeyboardButton("🎯 Актив",     callback_data="choose_symbol"),
            InlineKeyboardButton("⚙️ Режим",     callback_data="choose_mode"),
        ],
        [
            InlineKeyboardButton("📈 Статистика", callback_data="stats"),
        ],
    ])


def symbol_keyboard():
    buttons = []
    row = []
    for i, s in enumerate(SYMBOLS):
        row.append(InlineKeyboardButton(s, callback_data=f"sym_{s}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("◀️ Назад", callback_data="back")])
    return InlineKeyboardMarkup(buttons)


def mode_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🟢 Новичок",   callback_data="mode_Новичок")],
        [InlineKeyboardButton("🔵 Уверенный", callback_data="mode_Уверенный")],
        [InlineKeyboardButton("🔴 Про",       callback_data="mode_Про")],
        [InlineKeyboardButton("◀️ Назад",     callback_data="back")],
    ])


def format_signal(data: dict) -> str:
    signal   = data.get("signal", "NO SIGNAL")
    conf     = data.get("confidence", 0)
    symbol   = data.get("symbol", "")
    tf       = data.get("timeframe", "")
    reasons  = data.get("reasons", [])
    entry    = data.get("entry_price")
    win_rate = data.get("win_rate", 0)

    if signal == "UP":
        emoji = "🟢"
        arrow = "⬆️"
    elif signal == "DOWN":
        emoji = "🔴"
        arrow = "⬇️"
    else:
        emoji = "⚪"
        arrow = "➖"

    entry_str   = f"\n💰 Цена входа: `{entry:.2f}`" if entry else ""
    reasons_str = "\n".join(f"  • {r}" for r in reasons[:4])

    return (
        f"{emoji} *{signal}* {arrow}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📌 Актив: *{symbol}*\n"
        f"⏱ Таймфрейм: *{tf}*\n"
        f"💪 Уверенность: *{conf}%*"
        f"{entry_str}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📋 Причины:\n{reasons_str}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📊 Win Rate: *{win_rate}%*"
    )


def format_scan(data: dict) -> str:
    best    = data.get("best")
    reason  = data.get("reason", "")
    results = data.get("results", [])

    if not best:
        return f"🔍 *AI Сканер*\n\n⚪ {reason}"

    signal = best.get("signal", "")
    emoji  = "🟢" if signal == "UP" else "🔴"

    rows = ""
    for r in results:
        s  = r.get("signal", "")
        c  = r.get("confidence", 0)
        tf = r.get("timeframe", "")
        is_best = best.get("timeframe") == tf
        icon   = "🏆 " if is_best else "   "
        s_icon = "🟢" if s == "UP" else ("🔴" if s == "DOWN" else "⚪")
        rows  += f"{icon}{tf}: {s_icon} {s} {c if c > 0 else '--'}%\n"

    return (
        f"🤖 *AI Сканер — {best.get('symbol', '')}*\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🏆 Лучший вход: {emoji} *{signal} {best.get('timeframe')}* — *{best.get('confidence')}%*\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"*Все таймфреймы:*\n"
        f"`{rows}`"
        f"━━━━━━━━━━━━━━━━\n"
        f"💡 {reason}"
    )


async def get_signal(symbol: str, timeframe: str, mode: str) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(f"{BACKEND}/signal", json={
            "symbol": symbol, "timeframe": timeframe, "mode": mode
        })
        return resp.json()


async def get_scan(symbol: str, mode: str) -> dict:
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(f"{BACKEND}/scan", json={
            "symbol": symbol, "timeframe": "M1", "mode": mode
        })
        return resp.json()


async def get_stats() -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{BACKEND}/history")
        return resp.json()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 *Привет! Я твой сигнальный бот.*\n\n"
        f"🎯 Актив: *{user_state['symbol']}*\n"
        f"⚙️ Режим: *{user_state['mode']}*\n\n"
        "Выбери действие:"
    )
    await update.message.reply_text(
        text, parse_mode="Markdown", reply_markup=main_keyboard()
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data  = query.data

    if data.startswith("signal_"):
        tf = data.split("_")[1]
        await query.edit_message_text(
            f"⏳ Анализирую *{user_state['symbol']}* на {tf}...",
            parse_mode="Markdown"
        )
        try:
            result = await get_signal(user_state["symbol"], tf, user_state["mode"])
            text   = format_signal(result)
        except Exception as e:
            text = f"❌ Ошибка: {e}"
        await query.edit_message_text(
            text, parse_mode="Markdown", reply_markup=main_keyboard()
        )

    elif data == "scan":
        await query.edit_message_text(
            f"🔍 Сканирую все таймфреймы для *{user_state['symbol']}*...\n"
            f"Это займёт ~15 секунд.",
            parse_mode="Markdown"
        )
        try:
            result = await get_scan(user_state["symbol"], user_state["mode"])
            text   = format_scan(result)
        except Exception as e:
            text = f"❌ Ошибка: {e}"
        await query.edit_message_text(
            text, parse_mode="Markdown", reply_markup=main_keyboard()
        )

    elif data == "stats":
        try:
            stats    = await get_stats()
            total    = stats.get("total", 0)
            win_rate = stats.get("win_rate", 0)
            history  = stats.get("history", [])
            wins     = sum(1 for h in history if h.get("result") == "WIN")
            losses   = sum(1 for h in history if h.get("result") == "LOSS")
            text = (
                f"📊 *Статистика*\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"📈 Win Rate: *{win_rate}%*\n"
                f"✅ Побед: *{wins}*\n"
                f"❌ Поражений: *{losses}*\n"
                f"📝 Всего сигналов: *{total}*"
            )
        except Exception as e:
            text = f"❌ Ошибка: {e}"
        await query.edit_message_text(
            text, parse_mode="Markdown", reply_markup=main_keyboard()
        )

    elif data == "choose_symbol":
        await query.edit_message_text(
            "🎯 Выбери актив:", reply_markup=symbol_keyboard()
        )

    elif data.startswith("sym_"):
        symbol = data[4:]
        user_state["symbol"] = symbol
        await query.edit_message_text(
            f"✅ Актив выбран: *{symbol}*\n\nВыбери действие:",
            parse_mode="Markdown", reply_markup=main_keyboard()
        )

    elif data == "choose_mode":
        await query.edit_message_text(
            "⚙️ Выбери режим:", reply_markup=mode_keyboard()
        )

    elif data.startswith("mode_"):
        mode = data[5:]
        user_state["mode"] = mode
        await query.edit_message_text(
            f"✅ Режим: *{mode}*\n\nВыбери действие:",
            parse_mode="Markdown", reply_markup=main_keyboard()
        )

    elif data == "back":
        await query.edit_message_text(
            f"🎯 Актив: *{user_state['symbol']}*\n"
            f"⚙️ Режим: *{user_state['mode']}*\n\n"
            "Выбери действие:",
            parse_mode="Markdown", reply_markup=main_keyboard()
        )


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    logger.info("Бот запущен!")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()