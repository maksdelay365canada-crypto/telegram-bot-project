import logging
import os
from datetime import datetime, timezone

import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters,
)

# ── Настройки ──
BOT_TOKEN    = os.getenv("BOT_TOKEN", "7796005388:AAGu2HYvBRujBIfu4K2DzTxgr3ZFlHW3D80")
CHAT_ID      = 884778391
PORT         = os.getenv("PORT", "8000")
BACKEND      = os.getenv("BACKEND_URL", f"http://127.0.0.1:{PORT}")
MINI_APP_URL = os.getenv("MINI_APP_URL", "https://leafy-crostata-88c707.netlify.app")

MAX_DOGON_STEPS = 5

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

user_state = {
    "symbol":        "Bitcoin OTC",
    "mode":          "Уверенный",
    "initial_bet":   None,   # начальная ставка серии
    "current_bet":   None,   # текущая ставка (удваивается при догоне)
    "dogon_active":  False,  # включён ли режим догона
    "dogon_step":    0,      # текущий шаг догона (0 = не в серии)
    "awaiting_bet":  False,  # ждём ввода ставки от пользователя
}

SYMBOLS = [
    "Bitcoin OTC", "Ethereum OTC", "Solana OTC", "BNB OTC",
    "EUR/USD OTC", "GBP/USD OTC", "Gold OTC", "Brent Oil OTC",
    "Tesla OTC", "Apple OTC", "Amazon OTC",
]


# ── Клавиатуры ──

def main_keyboard():
    dogon_label = (
        f"🔄 Догон ВКЛ (шаг {user_state['dogon_step']})" if user_state["dogon_active"]
        else "🔄 Догон ВЫКЛ"
    )
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Открыть Mini App", web_app=WebAppInfo(url=MINI_APP_URL))],
        [
            InlineKeyboardButton("📊 Сигнал M1", callback_data="signal_M1"),
            InlineKeyboardButton("📊 Сигнал M5", callback_data="signal_M5"),
        ],
        [InlineKeyboardButton("🤖 AI Сканер", callback_data="scan")],
        [
            InlineKeyboardButton("🎯 Актив",     callback_data="choose_symbol"),
            InlineKeyboardButton("⚙️ Режим",     callback_data="choose_mode"),
        ],
        [InlineKeyboardButton(dogon_label,         callback_data="dogon_menu")],
        [InlineKeyboardButton("📈 Статистика",     callback_data="stats")],
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


def dogon_keyboard():
    bet_str = f"{user_state['current_bet']:.2f}" if user_state["current_bet"] else "не задана"
    toggle_label = "❌ Выключить догон" if user_state["dogon_active"] else "✅ Включить догон"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"💵 Ставка: {bet_str} — изменить", callback_data="set_bet")],
        [InlineKeyboardButton(toggle_label, callback_data="dogon_toggle")],
        [InlineKeyboardButton("🔄 Сбросить серию",  callback_data="dogon_reset")],
        [InlineKeyboardButton("◀️ Назад",           callback_data="back")],
    ])


# ── Форматирование ──

def format_signal(data: dict, bet: float = None) -> str:
    signal   = data.get("signal", "NO SIGNAL")
    conf     = data.get("confidence", 0)
    symbol   = data.get("symbol", "")
    tf       = data.get("timeframe", "")
    reasons  = data.get("reasons", [])
    entry    = data.get("entry_price")
    win_rate = data.get("win_rate", 0)
    expiry   = data.get("expiry_time")

    if signal == "UP":
        emoji, arrow = "🟢", "⬆️"
    elif signal == "DOWN":
        emoji, arrow = "🔴", "⬇️"
    else:
        emoji, arrow = "⚪", "➖"

    entry_str = f"\n💰 Цена входа: `{entry:.5f}`" if entry else ""

    expiry_str = ""
    if expiry:
        try:
            dt = datetime.fromisoformat(expiry.replace("Z", "+00:00"))
            expiry_str = f"\n⏰ Экспирация: *{dt.strftime('%H:%M:%S')} UTC*"
        except Exception:
            pass

    bet_str = f"\n💵 Ставка: *{bet:.2f}*" if bet else ""
    reasons_str = "\n".join(f"  • {r}" for r in reasons[:4])

    return (
        f"{emoji} *{signal}* {arrow}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📌 Актив: *{symbol}*\n"
        f"⏱ Таймфрейм: *{tf}*"
        f"{expiry_str}"
        f"{entry_str}"
        f"{bet_str}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📋 Причины:\n{reasons_str}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"💪 Уверенность: *{conf}%* | 📊 Win Rate: *{win_rate}%*"
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
        s      = r.get("signal", "")
        c      = r.get("confidence", 0)
        tf     = r.get("timeframe", "")
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


# ── API вызовы ──

async def api_signal(symbol: str, timeframe: str, mode: str) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(f"{BACKEND}/signal", json={
            "symbol": symbol, "timeframe": timeframe, "mode": mode
        })
        return resp.json()


async def api_scan(symbol: str, mode: str) -> dict:
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(f"{BACKEND}/scan", json={
            "symbol": symbol, "timeframe": "M1", "mode": mode
        })
        return resp.json()


async def api_stats() -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{BACKEND}/history")
        return resp.json()


async def api_price(symbol: str) -> float | None:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{BACKEND}/price", params={"symbol": symbol})
        return resp.json().get("price")


# ── Джоб: проверка результата и догон ──

async def check_result_job(context: ContextTypes.DEFAULT_TYPE):
    d           = context.job.data
    symbol      = d["symbol"]
    direction   = d["signal"]      # "UP" или "DOWN"
    entry_price = d["entry_price"]
    chat_id     = d["chat_id"]
    bet         = d["bet"]
    timeframe   = d["timeframe"]

    try:
        current_price = await api_price(symbol)
    except Exception:
        current_price = None

    if current_price is None:
        await context.bot.send_message(chat_id, "⚠️ Не удалось получить цену для проверки результата.")
        return

    won = (
        (direction == "UP"   and current_price > entry_price) or
        (direction == "DOWN" and current_price < entry_price)
    )
    change_pct = abs(current_price - entry_price) / entry_price * 100

    if won:
        profit = round(bet * 0.8, 2)
        text = (
            f"✅ *WIN!*\n"
            f"📊 {entry_price:.5f} → {current_price:.5f} ({change_pct:.2f}%)\n"
            f"💰 Прибыль: *+{profit}*\n"
            f"📌 {symbol}"
        )
        # сбрасываем серию
        user_state["current_bet"]  = user_state["initial_bet"]
        user_state["dogon_step"]   = 0
        await context.bot.send_message(chat_id, text, parse_mode="Markdown",
                                       reply_markup=main_keyboard())
    else:
        text = (
            f"❌ *LOSS*\n"
            f"📊 {entry_price:.5f} → {current_price:.5f} ({change_pct:.2f}%)\n"
            f"💸 Потеря: *-{bet:.2f}*\n"
            f"📌 {symbol}"
        )

        dogon_active = user_state["dogon_active"] and user_state["initial_bet"]
        over_limit   = user_state["dogon_step"] >= MAX_DOGON_STEPS

        if dogon_active and not over_limit:
            new_step = user_state["dogon_step"] + 1
            new_bet  = round(bet * 2, 2)
            user_state["current_bet"] = new_bet
            user_state["dogon_step"]  = new_step

            await context.bot.send_message(
                chat_id,
                text + f"\n\n🔄 *Догон — шаг {new_step}/{MAX_DOGON_STEPS}*\n"
                       f"Новая ставка: *{new_bet}*\nПолучаю сигнал...",
                parse_mode="Markdown",
            )

            try:
                result = await api_signal(symbol, timeframe, user_state["mode"])
            except Exception as e:
                await context.bot.send_message(chat_id, f"❌ Ошибка: {e}")
                return

            if result["signal"] in ("UP", "DOWN"):
                await context.bot.send_message(
                    chat_id,
                    format_signal(result, new_bet),
                    parse_mode="Markdown",
                    reply_markup=main_keyboard(),
                )
                _schedule_check(context, result, chat_id, new_bet, timeframe)
            else:
                await context.bot.send_message(
                    chat_id,
                    f"⚪ Нет чёткого сигнала для догона.\n"
                    f"{result.get('reasons', [''])[0]}\n\nДогон приостановлен.",
                    reply_markup=main_keyboard(),
                )
                user_state["dogon_active"] = False

        else:
            if over_limit:
                text += f"\n\n⚠️ Лимит догона достигнут ({MAX_DOGON_STEPS} шагов). Серия сброшена."
                user_state["current_bet"] = user_state["initial_bet"]
                user_state["dogon_step"]  = 0
                user_state["dogon_active"] = False
            await context.bot.send_message(chat_id, text, parse_mode="Markdown",
                                           reply_markup=main_keyboard())


def _schedule_check(context, result: dict, chat_id: int, bet: float, timeframe: str):
    """Планирует проверку результата в момент экспирации + 10 сек."""
    expiry = result.get("expiry_time")
    delay  = 70  # запасной вариант
    if expiry:
        try:
            dt    = datetime.fromisoformat(expiry.replace("Z", "+00:00"))
            secs  = (dt - datetime.now(timezone.utc)).total_seconds()
            delay = max(int(secs) + 10, 15)
        except Exception:
            pass

    context.job_queue.run_once(
        check_result_job,
        when=delay,
        data={
            "symbol":      result["symbol"],
            "signal":      result["signal"],
            "entry_price": result["entry_price"],
            "chat_id":     chat_id,
            "bet":         bet,
            "timeframe":   timeframe,
        },
    )


# ── Handlers ──

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 *Привет! Я твой сигнальный бот.*\n\n"
        f"🎯 Актив: *{user_state['symbol']}*\n"
        f"⚙️ Режим: *{user_state['mode']}*\n\n"
        "Выбери действие:"
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_keyboard())


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query   = update.callback_query
    await query.answer()
    data    = query.data
    chat_id = query.message.chat.id

    # ── Сигнал ──
    if data.startswith("signal_"):
        tf  = data.split("_")[1]
        bet = user_state["current_bet"]
        await query.edit_message_text(
            f"⏳ Анализирую *{user_state['symbol']}* на {tf}...",
            parse_mode="Markdown",
        )
        try:
            result = await api_signal(user_state["symbol"], tf, user_state["mode"])
            text   = format_signal(result, bet)
        except Exception as e:
            text   = f"❌ Ошибка: {e}"
            result = None

        await query.edit_message_text(text, parse_mode="Markdown",
                                      reply_markup=main_keyboard())

        # Планируем проверку если есть догон и реальный сигнал
        if (result and result.get("signal") in ("UP", "DOWN")
                and user_state["dogon_active"] and bet):
            _schedule_check(context, result, chat_id, bet, tf)

    # ── AI Сканер ──
    elif data == "scan":
        await query.edit_message_text(
            f"🔍 Сканирую все таймфреймы для *{user_state['symbol']}*...\n"
            f"Это займёт ~15 секунд.",
            parse_mode="Markdown",
        )
        try:
            result = await api_scan(user_state["symbol"], user_state["mode"])
            text   = format_scan(result)
        except Exception as e:
            text = f"❌ Ошибка: {e}"
        await query.edit_message_text(text, parse_mode="Markdown",
                                      reply_markup=main_keyboard())

    # ── Статистика ──
    elif data == "stats":
        try:
            stats    = await api_stats()
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
        await query.edit_message_text(text, parse_mode="Markdown",
                                      reply_markup=main_keyboard())

    # ── Выбор актива ──
    elif data == "choose_symbol":
        await query.edit_message_text("🎯 Выбери актив:", reply_markup=symbol_keyboard())

    elif data.startswith("sym_"):
        user_state["symbol"] = data[4:]
        await query.edit_message_text(
            f"✅ Актив: *{user_state['symbol']}*\n\nВыбери действие:",
            parse_mode="Markdown", reply_markup=main_keyboard(),
        )

    # ── Выбор режима ──
    elif data == "choose_mode":
        await query.edit_message_text("⚙️ Выбери режим:", reply_markup=mode_keyboard())

    elif data.startswith("mode_"):
        user_state["mode"] = data[5:]
        await query.edit_message_text(
            f"✅ Режим: *{user_state['mode']}*\n\nВыбери действие:",
            parse_mode="Markdown", reply_markup=main_keyboard(),
        )

    # ── Меню догона ──
    elif data == "dogon_menu":
        bet_str     = f"{user_state['current_bet']:.2f}" if user_state["current_bet"] else "не задана"
        cur_bet_str = f"{user_state['current_bet']:.2f}" if user_state["current_bet"] else "—"
        step_str    = f"{user_state['dogon_step']}/{MAX_DOGON_STEPS}" if user_state["dogon_step"] else "0"
        status      = "✅ ВКЛ" if user_state["dogon_active"] else "❌ ВЫКЛ"
        text = (
            f"🔄 *Система догонов*\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"Статус: *{status}*\n"
            f"Начальная ставка: *{bet_str}*\n"
            f"Текущий шаг: *{step_str}*\n"
            f"Текущая ставка: *{cur_bet_str}*\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"При LOSS ставка удваивается автоматически.\n"
            f"Лимит: {MAX_DOGON_STEPS} шагов подряд."
        )
        await query.edit_message_text(text, parse_mode="Markdown",
                                      reply_markup=dogon_keyboard())

    elif data == "set_bet":
        user_state["awaiting_bet"] = True
        await query.edit_message_text(
            "💵 Введи начальную ставку числом (например: `100`):",
            parse_mode="Markdown",
        )

    elif data == "dogon_toggle":
        if not user_state["current_bet"]:
            await query.answer("Сначала задай ставку!", show_alert=True)
            return
        user_state["dogon_active"] = not user_state["dogon_active"]
        if not user_state["dogon_active"]:
            user_state["dogon_step"]  = 0
            user_state["current_bet"] = user_state["initial_bet"]
        status = "✅ включён" if user_state["dogon_active"] else "❌ выключен"
        await query.edit_message_text(
            f"🔄 Догон {status}.\n\nВыбери действие:",
            parse_mode="Markdown", reply_markup=main_keyboard(),
        )

    elif data == "dogon_reset":
        user_state["dogon_step"]  = 0
        user_state["current_bet"] = user_state["initial_bet"]
        await query.edit_message_text(
            "🔄 Серия сброшена. Ставка возвращена к начальной.\n\nВыбери действие:",
            reply_markup=main_keyboard(),
        )

    elif data == "back":
        await query.edit_message_text(
            f"🎯 Актив: *{user_state['symbol']}*\n"
            f"⚙️ Режим: *{user_state['mode']}*\n\n"
            "Выбери действие:",
            parse_mode="Markdown", reply_markup=main_keyboard(),
        )


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает текстовые сообщения — используется для ввода ставки."""
    if not user_state["awaiting_bet"]:
        return
    try:
        amount = float(update.message.text.replace(",", ".").strip())
        if amount <= 0:
            raise ValueError
        user_state["initial_bet"]  = amount
        user_state["current_bet"]  = amount
        user_state["dogon_step"]   = 0
        user_state["awaiting_bet"] = False
        await update.message.reply_text(
            f"✅ Ставка установлена: *{amount:.2f}*\n\nВключи догон в меню 🔄",
            parse_mode="Markdown", reply_markup=main_keyboard(),
        )
    except ValueError:
        await update.message.reply_text("⚠️ Введи число, например: `100` или `25.50`",
                                        parse_mode="Markdown")


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    logger.info("Бот запущен!")
    application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
