import time
from aiogram.enums import ParseMode


async def process_broadcast_input(
    *,
    message,
    bot,
    waiting_for_broadcast: set,
    admin_panel_msg_id: dict,
    build_admin_kb,
    broadcast_to_all,
):
    chat_id = message.chat.id
    if message.text and message.text.strip().lower() in ["отмена", "отменить"]:
        waiting_for_broadcast.discard(chat_id)
        await bot.edit_message_text(
            "Добро пожаловать в админ-панель",
            chat_id=chat_id,
            message_id=admin_panel_msg_id[chat_id],
            reply_markup=build_admin_kb(),
        )
        await message.answer("Отменено.")
        return

    sent, failed = await broadcast_to_all(message.chat.id, message.message_id)
    waiting_for_broadcast.discard(chat_id)
    await bot.edit_message_text(
        "Добро пожаловать в админ-панель",
        chat_id=chat_id,
        message_id=admin_panel_msg_id[chat_id],
        reply_markup=build_admin_kb(),
    )
    await message.answer(f"📢 Рассылка завершена\nОтправлено: {sent}\nОшибок: {failed}")


async def process_supp_id_input(
    *,
    message,
    bot,
    waiting_for_supp_id: set,
    admin_panel_msg_id: dict,
    build_admin_kb,
    user_store: dict,
    active_supp: dict,
):
    chat_id = message.chat.id
    text = message.text.strip().lower()
    if text in ["отмена", "отменить"]:
        waiting_for_supp_id.discard(chat_id)
        await bot.edit_message_text(
            "Добро пожаловать в админ-панель",
            chat_id=chat_id,
            message_id=admin_panel_msg_id[chat_id],
            reply_markup=build_admin_kb(),
        )
        await message.answer("Отменено.")
        return

    try:
        target_id = int(text)
    except ValueError:
        await message.answer("Неверный ID, попробуйте снова или отмена.")
        return

    target_str = str(target_id)
    if target_str not in user_store:
        await message.answer("Такого пользователя нет.")
        return

    active_supp[message.from_user.id] = target_id
    waiting_for_supp_id.discard(chat_id)
    await bot.edit_message_text(
        "Добро пожаловать в админ-панель",
        chat_id=chat_id,
        message_id=admin_panel_msg_id[chat_id],
        reply_markup=build_admin_kb(),
    )
    await message.answer(f"🎯 Переписка с → {target_id} активирована (/supp_stop для остановки)")


async def process_schedule_input(
    *,
    message,
    waiting_for_schedule_time: set,
    user_store: dict,
    save_users,
):
    chat_id = message.chat.id
    uid = str(message.from_user.id)
    text = message.text.strip().lower()

    if text == "отменить рассылку" or text == "отмена":
        if uid in user_store:
            user_store[uid].pop("schedule_time", None)
            save_users(user_store)

        waiting_for_schedule_time.discard(chat_id)
        await message.answer("✅ Рассылка отключена.")
        return

    try:
        if ":" not in text:
            raise ValueError

        h_str, m_str = text.split(":")
        h, m = int(h_str), int(m_str)
        if not (0 <= h < 24 and 0 <= m < 60):
            raise ValueError

        formatted_time = f"{h:02d}:{m:02d}"
        if uid not in user_store:
            user_store[uid] = {}

        user_store[uid]["username"] = message.from_user.username or user_store[uid].get("username", "unknown")
        user_store[uid]["schedule_time"] = formatted_time
        user_store[uid]["last_activity"] = time.time()
        save_users(user_store)

        waiting_for_schedule_time.discard(chat_id)
        await message.answer(
            f"✅ Успешно! Теперь каждый день в <b>{formatted_time}</b> я буду присылать вам расписание (если есть пары).",
            parse_mode=ParseMode.HTML,
        )
    except ValueError:
        await message.answer(
            "⚠️ Неверный формат. Пожалуйста, введите время как <b>08:30</b> или напишите 'Отмена'.",
            parse_mode=ParseMode.HTML,
        )


async def process_broadtask_command(*, message, save_settings, set_broadtask):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(
            "⚠️ Использование:\n`/broadtask Текст` — установить\n`/broadtask clear` — удалить",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    payload = args[1].strip()
    if payload.lower() == "clear":
        set_broadtask("")
        save_settings()
        await message.answer("✅ Оповещение полностью удалено.")
    else:
        set_broadtask(payload)
        save_settings()
        await message.answer(f"✅ Новое оповещение установлено:\n\n{payload}")


async def process_broadtask_input(
    *,
    message,
    bot,
    waiting_for_broadtask: set,
    admin_panel_msg_id: dict,
    build_admin_kb,
    save_settings,
    set_broadtask,
):
    chat_id = message.chat.id
    waiting_for_broadtask.discard(chat_id)

    if message.text and message.text.strip().lower() in ["отмена", "отменить"]:
        await message.answer("Изменение текста отменено.")
        await bot.edit_message_text(
            "Добро пожаловать в админ-панель",
            chat_id=chat_id,
            message_id=admin_panel_msg_id[chat_id],
            reply_markup=build_admin_kb(),
        )
        return

    input_text = message.text.strip() if message.text else ""
    if input_text.lower() == "clear":
        set_broadtask("")
        confirm_msg = "✅ Дополнительный текст удален."
    else:
        set_broadtask(input_text)
        confirm_msg = f"✅ Текст успешно установлен:\n\n{input_text}"

    save_settings()
    await bot.edit_message_text(
        "Добро пожаловать в админ-панель",
        chat_id=chat_id,
        message_id=admin_panel_msg_id[chat_id],
        reply_markup=build_admin_kb(),
    )
    await message.answer(confirm_msg)

