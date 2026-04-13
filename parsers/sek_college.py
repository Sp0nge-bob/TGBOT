# parsers/sek_college.py

import re
from datetime import datetime
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import requests
from pathlib import Path

from .base import ScheduleParser, ScheduleData, LessonInfo


class SEKCollegeParser(ScheduleParser):
    """Парсер расписания СЭК колледжа"""
    
    BASE_URL = "https://sek-kampus.ru"
    SCHEDULE_PAGE = f"{BASE_URL}/studentu/raspisanie/"
    SCHEDULE_FILES_DIR = f"{BASE_URL}/doc/raspisaniya/alx_rasp"
    
    # Факультеты и их префиксы в HTML файлах
    FACULTIES = {
        "[S]": "Факультет строительных технологий",
        "[G]": "Факультет инженерных изысканий",
        "[T]": "Факультет наземного транспорта",
        "[E]": "Факультет электро- и теплоэнергетики",
    }
    
    # Дни недели в расписании
    DAYS_MAP = {
        "ПОНЕДЕЛЬНИК": "понедельник",
        "ВТОРНИК": "вторник",
        "СРЕДА": "среда",
        "ЧЕТВЕРГ": "четверг",
        "ПЯТНИЦА": "пятница",
        "СУББОТА": "суббота",
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        })
        self._groups_cache: Optional[List[str]] = None
    
    def get_name(self) -> str:
        return "СЭК им. П. Мачнева"
    
    def get_groups(self) -> List[str]:
        """Получить все группы со страницы расписания"""
        if self._groups_cache:
            return self._groups_cache
        
        try:
            response = self.session.get(self.SCHEDULE_PAGE, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            groups = []
            
            # Найди все кнопки с классом "grplink"
            for button in soup.find_all('button', class_='grplink'):
                onclick = button.get('onclick', '')
                # onclick="alxfun2('[S]-(1)-ЖКХ11','doc/raspisaniya/alx_rasp/[S]-(1)-ЖКХ11.html');"
                match = re.search(r"alxfun2\('([^']+)'", onclick)
                if match:
                    group_id = match.group(1)
                    # Извлеки название группы
                    group_name = group_id.split('-')[-1]
                    if group_name not in groups:
                        groups.append(group_name)
            
            self._groups_cache = sorted(groups)
            return self._groups_cache
            
        except Exception as e:
            print(f"Ошибка при получении групп: {e}")
            return []
    
    def parse_schedule(self, group: str) -> ScheduleData:
        """Спарсить расписание для конкретной группы"""
        
        # Найди полный ID группы
        group_id = self._find_group_id(group)
        if not group_id:
            raise ValueError(f"Группа {group} не найдена")
        
        # Загрузи HTML файл расписания
        file_url = f"{self.SCHEDULE_FILES_DIR}/{group_id}.html"
        
        try:
            response = self.session.get(file_url, timeout=10)
            response.encoding = 'utf-8'
        except Exception as e:
            raise Exception(f"Не удалось загрузить расписание: {e}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Парсируй таблицу с расписанием
        schedule = self._parse_table(soup)
        
        # Определи четность недели (из основной страницы)
        week_parity = self._get_week_parity()
        
        return ScheduleData(
            group=group,
            college="sek",
            schedule=schedule,
            updated_at=datetime.now(),
            week_parity=week_parity,
        )
    
    def _find_group_id(self, group_name: str) -> Optional[str]:
        """Найти полный ID группы по названию"""
        groups_html = self.session.get(self.SCHEDULE_PAGE).text
        
        # Ищи в onclick атрибутах
        pattern = rf"alxfun2\('([^']*{re.escape(group_name)}[^']*)',"
        match = re.search(pattern, groups_html)
        
        if match:
            return match.group(1)
        return None
    
    def _parse_table(self, soup: BeautifulSoup) -> Dict[str, List[LessonInfo]]:
        """Парсить таблицу с расписан��ем"""
        schedule = {}
        
        # Найди основную таблицу расписания
        tables = soup.find_all('table', class_='table-all')
        if not tables:
            return schedule
        
        current_day = None
        
        for table in tables:
            rows = table.find_all('tr')
            
            for row in rows:
                cells = row.find_all('td')
                
                if not cells:
                    continue
                
                # Проверь если это строка с днем недели
                cell_text = cells[0].get_text(strip=True).upper()
                
                if cell_text in self.DAYS_MAP:
                    current_day = self.DAYS_MAP[cell_text]
                    if current_day not in schedule:
                        schedule[current_day] = []
                    continue
                
                # Пропусти заголовки таблицы
                if cell_text == "№":
                    continue
                
                # Парсируй занятие
                if current_day and cell_text.isdigit():
                    try:
                        lesson_num = int(cell_text)
                        subject = cells[1].get_text(strip=True)
                        room = cells[2].get_text(strip=True)
                        teacher = cells[3].get_text(strip=True)
                        
                        # Пропусти пустые занятия
                        if subject:
                            lesson = LessonInfo(
                                number=lesson_num,
                                subject=subject,
                                room=room,
                                teacher=teacher,
                            )
                            schedule[current_day].append(lesson)
                    except (IndexError, ValueError):
                        continue
        
        return schedule
    
    def _get_week_parity(self) -> str:
        """Получить четность недели со страницы"""
        try:
            response = self.session.get(self.SCHEDULE_PAGE, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищи элемент с информацией о неделе
            week_info = soup.find(string=re.compile(r"(четн|нечетн)"))
            if week_info:
                if "четн" in week_info:
                    return "четная"
                elif "нечетн" in week_info:
                    return "нечетная"
        except:
            pass
        
        return "четная"  # По умолчанию
