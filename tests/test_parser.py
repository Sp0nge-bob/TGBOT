import unittest

from parser import get_current_week_from_html, parse_schedule_pretty


class ParserTests(unittest.TestCase):
    def test_parse_schedule_basic_lesson(self):
        html = """
        <table>
          <tr><h3>Понедельник 01.01</h3></tr>
          <tr>
            <td>1</td>
            <td>08:00-09:35</td>
            <td>Очная</td>
            <td>Математика<br/>Иванов И.И.<br/>Корпус А Кабинет: 101</td>
            <td>Тема 1</td>
            <td>moodle</td>
            <td>Задача 1</td>
          </tr>
        </table>
        """
        result = parse_schedule_pretty(html)
        self.assertIn("📅 <b>Понедельник 01.01</b>", result)
        self.assertIn("📚 Математика", result)
        self.assertIn("👤 Иванов И.И.", result)
        self.assertIn("🚪Кабинет: 101", result)

    def test_parse_schedule_replacement_flag(self):
        html = """
        <table>
          <tr><h3>Вторник 02.01</h3></tr>
          <tr>
            <td>2</td>
            <td>09:45-11:20</td>
            <td>Очная</td>
            <td><a class="t_zm">Замена</a><br/>Физика<br/>Петров П.П.<br/>Корпус Б Кабинет: 202</td>
            <td></td>
            <td></td>
            <td></td>
          </tr>
        </table>
        """
        result = parse_schedule_pretty(html)
        self.assertIn("(замена)", result)

    def test_extract_week_from_next_link(self):
        html = 'следующая неделя <a href="/?wk=16">вперёд</a>'
        self.assertEqual(get_current_week_from_html(html), 15)

    def test_extract_week_from_prev_link(self):
        html = 'предыдущая неделя <a href="/?wk=10">назад</a>'
        self.assertEqual(get_current_week_from_html(html), 11)

    def test_extract_week_from_fallback_number(self):
        html = "Сейчас идёт 7 неделя"
        self.assertEqual(get_current_week_from_html(html), 7)


if __name__ == "__main__":
    unittest.main()
