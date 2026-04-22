import asyncio
import datetime
import os

from aiogram.enums import ParseMode
from aiogram.types import FSInputFile


async def handle_admin_panel_action(
    *,
    action: str,
    cb,
    bot,
    chat_id: int,
    panel_id: int,
    build_admin_kb,
    get_stats_text,
    get_users_list_text,
    get_schedule_list_text,
    waiting_for_broadcast: set,
    waiting_for_broadtask: set,
    waiting_for_supp_id: set,
    waiting_for_backup_time: set,
    user_store: dict,
    selected_group_per_chat: dict,
    save_users,
    logger,
    get_broadtask,
    user_file: str,
    groups_file: str,
    selection_file: str,
    settings_file: str,
    cache_file: str,
    auto_backup_time: str,
    get_current_monday_ts,
    get_current_wk,
    current_wk_cache: dict,
):
    if action == "stats":
        text = get_stats_text()
        await bot.edit_message_text(
            text,
            chat_id=chat_id,
            message_id=panel_id,
            parse_mode=ParseMode.HTML,
            reply_markup=build_admin_kb(),
        )

    elif action == "users":
        text = get_users_list_text()
        await bot.edit_message_text(text, chat_id=chat_id, message_id=panel_id, reply_markup=build_admin_kb())

    elif action == "schedules":
        text = get_schedule_list_text()
        await bot.edit_message_text(
            text,
            chat_id=chat_id,
            message_id=panel_id,
            parse_mode=ParseMode.HTML if "<b>" in text else None,
            reply_markup=build_admin_kb(),
        )

    elif action == "broadcast":
        waiting_for_broadcast.add(chat_id)
        await bot.edit_message_text(
            "Напишите сообщение для массового оповещения, либо напишите отмена.",
            chat_id=chat_id,
            message_id=panel_id,
        )

    elif action == "bt_setup":
        waiting_for_broadtask.add(chat_id)
        broadtask = get_broadtask()
        current_status = f"\n\n<b>Текущий текст:</b>\n<i>{broadtask}</i>" if broadtask else "\n\n(Сейчас пусто)"
        await bot.edit_message_text(
            f"Введите текст, который будет автоматически добавляться в конец КАЖДОГО сообщения бота.{current_status}\n\n"
            f"Отправьте <b>clear</b>, чтобы удалить текст, или <b>отмена</b>.",
            chat_id=chat_id,
            message_id=panel_id,
            parse_mode=ParseMode.HTML,
        )

    elif action == "supp":
        lines = [f"{uid} — @{info.get('username', 'без ника')}" for uid, info in sorted(user_store.items(), key=lambda x: int(x[0]))]
        text = "📋 Список пользователей:\n\n" + "\n".join(lines) + "\n\nУкажите ID для связи (или отмена)"
        waiting_for_supp_id.add(chat_id)
        await bot.edit_message_text(text, chat_id=chat_id, message_id=panel_id)

    elif action == "clear_sent":
        count = 0
        for uid_str, info in user_store.items():
            if "last_sent_date" in info:
                del info["last_sent_date"]
                count += 1
        save_users(user_store)
        text = f"✅ <b>last_sent_date очищен у {count} пользователей!</b>\n\nТеперь рассылка сработает сегодня."
        await bot.edit_message_text(
            text,
            chat_id=chat_id,
            message_id=panel_id,
            parse_mode=ParseMode.HTML,
            reply_markup=build_admin_kb(),
        )
        logger.info(f"🧹 Админ очистил last_sent_date у {count} пользователей")

    elif action == "backup":
        await cb.answer("📦 Подготавливаем бэкап файлов...")
        files_to_send = {
            "users.json": user_file,
            "groups.json": groups_file,
            "selections.json": selection_file,
            "settings.json": settings_file,
            "page_cache.pkl": cache_file,
        }

        sent_count = 0
        for display_name, file_path in files_to_send.items():
            if os.path.exists(file_path):
                try:
                    document = FSInputFile(file_path)
                    await bot.send_document(
                        chat_id=chat_id,
                        document=document,
                        caption=f"💾 Бэкап: <b>{display_name}</b>\n📅 {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}",
                        parse_mode=ParseMode.HTML,
                    )
                    sent_count += 1
                    logger.info(f"✅ Отправлен бэкап: {display_name}")
                    await asyncio.sleep(0.6)
                except Exception as e:
                    logger.error(f"Ошибка отправки {display_name}: {e}")
                    await bot.send_message(
                        chat_id,
                        f"❌ Не удалось отправить <b>{display_name}</b>\nОшибка: {e}",
                        parse_mode=ParseMode.HTML,
                    )
            else:
                await bot.send_message(chat_id, f"⚠️ Файл <b>{display_name}</b> не найден", parse_mode=ParseMode.HTML)

        await bot.send_message(
            chat_id=chat_id,
            text=f"✅ <b>Бэкап завершён!</b>\n\nОтправлено файлов: <b>{sent_count}</b>/5",
            parse_mode=ParseMode.HTML,
        )
        logger.info(f"💾 Админ создал бэкап — успешно отправлено {sent_count} файлов")

    elif action == "set_backup_time":
        waiting_for_backup_time.add(chat_id)
        await bot.edit_message_text(
            f"⏰ Укажите время автобэкапа в формате <b>HH:MM</b>\n\n"
            f"Текущее время: <b>{auto_backup_time}</b>\n\n"
            f"Пример: <code>03:30</code> или <code>04:00</code>",
            chat_id=chat_id,
            message_id=panel_id,
            parse_mode=ParseMode.HTML,
        )

    elif action == "debug_week":
        monday_ts = get_current_monday_ts()
        current_wk = await get_current_wk()
        text = (
            f"🔍 <b>Отладка автоопределения недели</b>\n\n"
            f"📅 Сегодня: <b>{datetime.datetime.now().strftime('%A %d.%m.%Y %H:%M')}</b>\n\n"
            f"Понедельник этой недели (00:00): <b>{datetime.datetime.fromtimestamp(monday_ts).strftime('%d.%m.%Y %H:%M')}</b>\n"
            f"monday_ts = <code>{monday_ts}</code>\n\n"
            f"CURRENT_WK_CACHE:\n   wk = <b>{current_wk_cache['wk']}</b>\n   ts = <code>{current_wk_cache['ts']}</code>\n\n"
            f"✅ Определённая неделя: <b>{current_wk}</b>"
        )
        await bot.edit_message_text(
            text,
            chat_id=chat_id,
            message_id=panel_id,
            parse_mode=ParseMode.HTML,
            reply_markup=build_admin_kb(),
        )
        current_wk_cache["ts"] = 0
        logger.info("🔄 Кеш недели сброшен через админ-панель")

