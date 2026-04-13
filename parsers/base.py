# parsers/base.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

@dataclass
class LessonInfo:
    """Информация об одном занятии"""
    number: int
    subject: str
    room: str
    teacher: str
    lesson_type: str = "лекция"  # лекция, лаб, практика


@dataclass
class ScheduleData:
    """Данные расписания группы"""
    group: str
    college: str
    schedule: Dict[str, List[LessonInfo]]  # day -> lessons
    updated_at: datetime
    week_parity: str = "четная"  # четная/нечетная
    is_holiday: bool = False


class ScheduleParser(ABC):
    """
    Базовый класс для парсера расписания конкретного колледжа
    
    Каждый парсер должен реализовать эти методы
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """Название колледжа"""
        pass
    
    @abstractmethod
    def get_groups(self) -> List[str]:
        """Получить список всех групп"""
        pass
    
    @abstractmethod
    def parse_schedule(self, group: str) -> ScheduleData:
        """
        Спарсить расписание для группы
        
        Args:
            group: Название группы
            
        Returns:
            ScheduleData с расписанием
        """
        pass
    
    def format_day_name(self, day: int) -> str:
        """Форматировать номер дня недели в название"""
        days = {
            0: "понедельник",
            1: "вторник",
            2: "среда",
            3: "четверг",
            4: "пятница",
            5: "суббота",
            6: "воскресенье",
        }
        return days.get(day, "неизвестно")
