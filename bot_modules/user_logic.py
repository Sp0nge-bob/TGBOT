from aiogram.enums import ParseMode


def extract_today(schedule_text: str) -> str:
    days = [d.strip() for d in schedule_text.split("📅") if d.strip()]
    if not days:
        return "⚠️ День не найден"
    for d in days:
        if "суббота" not in d.lower():
            return "📅 " + d
    return "📅 " + days[0]


def has_classes_today(week_text: str) -> bool:
    today_text = extract_today(week_text).lower()
    return not ("занятий нет" in today_text or "день не найден" in today_text)


async def handle_show_week(*, message, wk, get_cached_page, shared_session, build_url_for_wk, parse_schedule_pretty, selected_group_per_chat, send_or_edit_text):
    chat_id = message.chat.id
    html = await get_cached_page(shared_session, build_url_for_wk(wk, chat_id))
    text = parse_schedule_pretty(html)
    group = selected_group_per_chat.get(chat_id, "не выбрана")
    text = f"👤 <b>Ваша группа:</b> {group}\n\n{text}"
    await send_or_edit_text(text, chat_id)


async def get_today_schedule_text(*, chat_id: int, selected_group_per_chat: dict, build_url_for_wk, get_cached_page, shared_session, parse_schedule_pretty) -> str:
    group = selected_group_per_chat.get(chat_id)
    if not group:
        return "⚠️ Сначала выбери группу командой /start"

    url = build_url_for_wk(None, chat_id)
    html = await get_cached_page(shared_session, url)
    if not html:
        return "❌ Не удалось загрузить расписание"

    week_text = parse_schedule_pretty(html)
    today_text = extract_today(week_text)
    return f"👤 <b>Ваша группа:</b> {group}\n\n{today_text}"


async def get_week_schedule_text(*, chat_id: int, selected_group_per_chat: dict, build_url_for_wk, get_cached_page, shared_session, parse_schedule_pretty) -> str:
    group = selected_group_per_chat.get(chat_id)
    if not group:
        return "⚠️ Сначала выбери группу командой /start"

    url = build_url_for_wk(None, chat_id)
    html = await get_cached_page(shared_session, url)
    if not html:
        return "❌ Не удалось загрузить расписание"

    week_text = parse_schedule_pretty(html)
    return f"👤 <b>Ваша группа:</b> {group}\n\n{week_text}"


async def process_cmd_today(*, message, selected_group_per_chat, get_current_wk, current_wk_per_chat, build_url_for_wk, get_cached_page, shared_session, parse_schedule_pretty, reply_markup):
    chat_id = message.chat.id
    group = selected_group_per_chat.get(chat_id)
    if not group:
        await message.answer("⚠️ Сначала выбери группу командой /start")
        return None

    wk = await get_current_wk()
    current_wk_per_chat[chat_id] = wk
    url = build_url_for_wk(wk, chat_id)
    html = await get_cached_page(shared_session, url)
    week_text = parse_schedule_pretty(html)
    today_text = extract_today(week_text)
    text = f"👤 <b>Ваша группа:</b> {group}\n\n{today_text}"
    msg = await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup())
    return msg, text


async def process_cmd_week(*, message, selected_group_per_chat, get_current_wk, current_wk_per_chat, build_url_for_wk, get_cached_page, shared_session, parse_schedule_pretty, reply_markup):
    chat_id = message.chat.id
    group = selected_group_per_chat.get(chat_id)
    if not group:
        await message.answer("⚠️ Сначала выбери группу командой /start")
        return None

    wk = await get_current_wk()
    current_wk_per_chat[chat_id] = wk
    url = build_url_for_wk(wk, chat_id)
    html = await get_cached_page(shared_session, url)
    week_text = parse_schedule_pretty(html)
    text = f"👤 <b>Ваша группа:</b> {group}\n\n{week_text}"
    msg = await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=reply_markup())
    return msg, text

