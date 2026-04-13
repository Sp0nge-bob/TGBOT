# parser.py
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
import re

# ====================== НАСТРОЙКА ======================
# ← Здесь меняй название парсера для логов
PARSER_NAME = "ПГУТИ Парсер"        # ← ← ← ТВОЁ НАЗВАНИЕ
# Примеры:
# PARSER_NAME = "КС ПГУТИ"
# PARSER_NAME = "lk.ks.psuti.ru Parser v2"
# PARSER_NAME = "My Custom Parser"


class ScheduleParser(ABC):
    """Базовый класс для всех парсеров"""
    
    @abstractmethod
    def parse_schedule(self, html: str) -> str:
        pass

    @abstractmethod
    def extract_current_week(self, html: str) -> int:
        pass

    def get_name(self) -> str:
        """Возвращает имя парсера для логов"""
        return PARSER_NAME


class PsutiScheduleParser(ScheduleParser):
    """Парсер для lk.ks.psuti.ru"""

    def parse_schedule(self, html: str) -> str:
        if not html or not html.strip():
            return "⚠️ Расписание не загрузилось"

        soup = BeautifulSoup(html, "html.parser")
        result = []
        last_day = None

        for tr in soup.find_all("tr"):
            h3 = tr.find("h3")
            if h3:
                day = " ".join(h3.get_text(" ", strip=True).split())
                if any(word in day.lower() for word in ["предыдущая", "выберите", "курс:"]):
                    continue
                if day != last_day:
                    if result:
                        result.append("\n")
                    result.append(f"📅 <b>{day}</b>\n")
                    last_day = day
                continue

            tds = tr.find_all("td", recursive=False)
            if len(tds) < 7 or not tds[0].get_text(strip=True).isdigit():
                continue

            num = tds[0].get_text(strip=True)
            time_str = " ".join(tds[1].stripped_strings).strip()
            way = tds[2].get_text(strip=True).strip()

            disc_td = tds[3]
            disc_text = disc_td.get_text(" ", strip=True)
            is_replacement = bool(disc_td.find("a", class_="t_zm") or "Замена" in disc_text)

            disc_parts = [line.strip() for line in disc_td.stripped_strings if line.strip()]
            discipline = disc_parts[0] if disc_parts else "Нет данных"
            teacher = disc_parts[1] if len(disc_parts) > 1 else ""
            location = " ".join(disc_parts[2:]).replace("Кабинет:", "🚪 Кабинет:") if len(disc_parts) > 2 else ""

            theme = " ".join(tds[4].stripped_strings).strip()
            resource = " ".join(tds[5].stripped_strings).strip()
            task = " ".join(tds[6].stripped_strings).strip()

            pair_lines = [f"▫️ <b>{num}</b> | {time_str}"]
            if way:
                pair_lines.append(f"   <i>{way}</i>")
            pair_lines.append(f"   📚 {discipline}")
            if is_replacement:
                pair_lines.append("   <i>(замена)</i>")
            if teacher:
                pair_lines.append(f"   👤 {teacher}")
            if location:
                if "🚪" in location:
                    addr, cab = location.split("🚪", 1)
                    pair_lines.append(f"   🏢 {addr.strip()}")
                    pair_lines.append(f"   🚪{cab.strip()}")
                else:
                    pair_lines.append(f"   🏢 {location}")
            if theme:
                pair_lines.append(f"   📌 <i>{theme}</i>")
            if resource:
                pair_lines.append(f"   🔗 {resource}")
            if task:
                pair_lines.append(f"   📝 {task}")

            result.append("\n".join(pair_lines))
            result.append("")

        return "\n".join(result).strip() or "Нет пар на эту неделю"

    def extract_current_week(self, html: str) -> int:
        # Основной способ — из ссылки "следующая неделя"
        next_match = re.search(r'следующая неделя.*?wk=(\d+)', html, re.IGNORECASE | re.DOTALL)
        if next_match:
            return int(next_match.group(1)) - 1

        prev_match = re.search(r'предыдущая неделя.*?wk=(\d+)', html, re.IGNORECASE | re.DOTALL)
        if prev_match:
            return int(prev_match.group(1)) + 1

        all_wk = re.findall(r'wk=(\d+)', html)
        if all_wk:
            return max(int(w) for w in all_wk)

        small_match = re.search(r'(\d+)\s*неделя', html, re.IGNORECASE)
        if small_match:
            return int(small_match.group(1))

        return 0


# ====================== ФАБРИКА ======================
def get_parser() -> ScheduleParser:
    """Возвращает активный парсер"""
    return PsutiScheduleParser()


# ====================== СОВМЕСТИМОСТЬ ======================
def parse_schedule_pretty(html: str) -> str:
    return get_parser().parse_schedule(html)


def get_current_week_from_html(html: str) -> int:
    return get_parser().extract_current_week(html)
