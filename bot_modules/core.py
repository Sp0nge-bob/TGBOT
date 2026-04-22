import asyncio
import datetime
import json
import os
import shutil
import tempfile
import time
from collections import Counter
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class RuntimeConfig:
    token: str | None
    proxy_url: str | None
    proxy_mode: str
    base_url: str
    owner_id: int
    user_file: str
    groups_file: str
    selection_file: str
    settings_file: str
    cache_file: str
    cache_ttl_seconds: int
    max_cache_age_days: int
    fetch_semaphore_limit: int
    locks_cache_max: int
    lk_limit_per_host: int
    callback_delay: float
    user_delay: float
    auto_backup_time: str
    auto_backup_enabled: bool


def load_runtime_config() -> RuntimeConfig:
    load_dotenv()
    owner_raw = os.getenv("OWNERID", "").strip()
    if not owner_raw.isdigit():
        raise RuntimeError("OWNERID не задан или некорректен. Укажи числовой Telegram ID в .env")

    return RuntimeConfig(
        token=os.getenv("RELEASE_TOKEN"),
        proxy_url=os.getenv("PROXY_URL"),
        proxy_mode=os.getenv("PROXY_MODE", "none").strip().lower(),
        base_url="https://lk.ks.psuti.ru/?mn=2&obj=218",
        owner_id=int(owner_raw),
        user_file="users.json",
        groups_file="groups.json",
        selection_file="selections.json",
        settings_file="settings.json",
        cache_file="page_cache.pkl",
        cache_ttl_seconds=1500,
        max_cache_age_days=1,
        fetch_semaphore_limit=15,
        locks_cache_max=1000,
        lk_limit_per_host=15,
        callback_delay=1.0,
        user_delay=1.0,
        auto_backup_time="03:00",
        auto_backup_enabled=True,
    )


def load_json_file(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}


def save_json_file(path: str, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_users(user_file: str, logger) -> dict:
    try:
        raw = load_json_file(user_file)
        return {str(k): v for k, v in raw.items()}
    except Exception as e:
        logger.error(f"Ошибка загрузки пользователей: {e}")
        return {}


def save_users(users: dict, user_file: str, logger):
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as tmp:
            json.dump(users, tmp, ensure_ascii=False, indent=2)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_path = tmp.name
        shutil.move(tmp_path, user_file)
    except Exception as e:
        logger.error(f"Ошибка атомарного сохранения users: {e}")
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


async def async_save_users(users: dict, user_file: str, logger):
    await asyncio.to_thread(save_users, users, user_file, logger)


def collect_stats(*, start_time: float, cache_size: int, user_store: dict, selected_group_per_chat: dict, total_requests: int, bot_owner_id: int) -> dict[str, str | int]:
    uptime_seconds = int(time.time() - start_time)
    uptime_str = str(datetime.timedelta(seconds=uptime_seconds))
    total_users = len(user_store)
    if selected_group_per_chat:
        most_popular_group, group_count = Counter(selected_group_per_chat.values()).most_common(1)[0]
    else:
        most_popular_group, group_count = "Нет данных", 0

    last_user_name = "Нет данных"
    last_time = 0
    for uid_str, info in user_store.items():
        if int(uid_str) == bot_owner_id:
            continue
        user_time = info.get("last_activity", 0)
        if user_time > last_time:
            last_time = user_time
            last_user_name = info.get("username", "без_ника")

    if last_time > 0:
        last_use_text = f"@{last_user_name} ({datetime.datetime.fromtimestamp(last_time).strftime('%d.%m.%Y %H:%M:%S')})"
    else:
        last_use_text = "Никто еще не пользовался"

    active_schedules = sum(1 for info in user_store.values() if "schedule_time" in info)
    today_iso = datetime.date.today().isoformat()
    today_sent = sum(1 for info in user_store.values() if info.get("last_sent_date") == today_iso)
    last_sent_info = None
    for uid_str, info in user_store.items():
        if info.get("last_sent_date") == today_iso and "last_sent_time" in info:
            if last_sent_info is None or info["last_sent_time"] > last_sent_info[1]:
                last_sent_info = (info.get("username", "без ника"), info["last_sent_time"], uid_str)
    last_sent_text = f"@{last_sent_info[0]} в {last_sent_info[1]}" if last_sent_info else "Сегодня ещё не было"

    return {
        "uptime_str": uptime_str,
        "cache_size": cache_size,
        "total_users": total_users,
        "most_popular_group": most_popular_group,
        "group_count": group_count,
        "total_reqs": total_requests,
        "last_use_text": last_use_text,
        "active_schedules": active_schedules,
        "today_sent": today_sent,
        "last_sent_text": last_sent_text,
    }


def render_stats_text(stats: dict[str, str | int]) -> str:
    return (
        f"📊 <b>Статистика бота</b>\n\n"
        f"⏱ <b>Время работы:</b> {stats['uptime_str']}\n"
        f"📦 <b>Размер кеша:</b> {stats['cache_size']} стр.\n"
        f"👥 <b>Всего юзеров:</b> {stats['total_users']}\n"
        f"🏆 <b>Популярная группа:</b> {stats['most_popular_group']} ({stats['group_count']} чел.)\n"
        f"📈 <b>Всего запросов:</b> {stats['total_reqs']}\n"
        f"👤 <b>Последний активный:</b> {stats['last_use_text']}\n"
        f"🔔 <b>Подключено рассылок:</b> {stats['active_schedules']}\n"
        f"📨 <b>Рассылок отправлено сегодня:</b> {stats['today_sent']}\n"
        f"⏰ <b>Последняя рассылка:</b> {stats['last_sent_text']}\n"
    )


async def broadcast_to_all(*, bot, user_store: dict, source_chat_id: int, source_message_id: int, delay_seconds: float = 0.05) -> tuple[int, int]:
    sent = 0
    failed = 0
    for uid in user_store:
        user_id = int(uid)
        try:
            await bot.copy_message(
                chat_id=user_id,
                from_chat_id=source_chat_id,
                message_id=source_message_id,
            )
            sent += 1
            await asyncio.sleep(delay_seconds)
        except Exception:
            failed += 1
    return sent, failed

