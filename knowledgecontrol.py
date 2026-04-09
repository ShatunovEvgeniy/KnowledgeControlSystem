"""
Модуль работы с базой данных и бизнес-логикой системы контроля знаний.
Содержит класс KnowledgeControlSystem для управления предметами, учащимися,
вопросами и результатами тестирования.
"""

import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any


class KnowledgeControlSystem:
    """
    Класс для управления системой контроля знаний учащихся.
    Работает с базой данных SQLite, хранящей информацию о предметах,
    вопросах, учащихся и результатах тестирования.
    """
    
    def __init__(self, db_path: str = "knowledge_control.db"):
        """
        Инициализация системы контроля знаний.
        
        Args:
            db_path: Путь к файлу базы данных SQLite
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
        self.create_tables()
    
    def _connect(self):
        """Установление соединения с базой данных."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            raise Exception(f"Ошибка подключения к базе данных: {e}")
    
    def create_tables(self):
        """
        Создание таблиц в базе данных.
        Создаёт таблицы: students, subjects, results.
        Таблицы вопросов создаются динамически для каждого предмета.
        """
        try:
            # Таблица учащихся
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    patronymic TEXT,
                    group_name TEXT NOT NULL,
                    birth_date TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица предметов
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS subjects (
                    subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject_name TEXT UNIQUE NOT NULL,
                    table_name TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица результатов тестирования
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS results (
                    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    subject_id INTEGER NOT NULL,
                    score INTEGER NOT NULL,
                    total_questions INTEGER NOT NULL,
                    percentage REAL NOT NULL,
                    test_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students(student_id),
                    FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
                )
            ''')
            
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"Ошибка создания таблиц: {e}")
    
    def _get_table_name(self, subject_name: str) -> str:
        """
        Получение имени таблицы вопросов для предмета.
        
        Args:
            subject_name: Название предмета
            
        Returns:
            Имя таблицы в формате questions_<subjectname>
        """
        return f"questions_{subject_name.lower().replace(' ', '_').replace('-', '_')}"
    
    # ==================== Методы работы с предметами ====================
    
    def add_subject(self, subject_name: str) -> Tuple[bool, str]:
        """
        Добавление нового предмета.
        
        Args:
            subject_name: Название предмета
            
        Returns:
            Кортеж (успех, сообщение)
        """
        if not subject_name or not subject_name.strip():
            return False, "Название предмета не может быть пустым"
        
        subject_name = subject_name.strip()
        table_name = self._get_table_name(subject_name)
        
        try:
            self.cursor.execute('''
                INSERT INTO subjects (subject_name, table_name)
                VALUES (?, ?)
            ''', (subject_name, table_name))
            
            # Создаём таблицу вопросов для этого предмета
            self.cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {table_name} (
                    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_number INTEGER NOT NULL,
                    question_text TEXT NOT NULL,
                    variant_a TEXT NOT NULL,
                    variant_b TEXT NOT NULL,
                    variant_c TEXT NOT NULL,
                    variant_d TEXT NOT NULL,
                    correct_answer TEXT NOT NULL CHECK(correct_answer IN ('A', 'B', 'C', 'D')),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.conn.commit()
            return True, f"Предмет '{subject_name}' успешно добавлен"
        except sqlite3.IntegrityError:
            return False, f"Предмет '{subject_name}' уже существует"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Ошибка добавления предмета: {e}"
    
    def get_all_subjects(self) -> List[Dict[str, Any]]:
        """
        Получение списка всех предметов.
        
        Returns:
            Список словарей с информацией о предметах
        """
        try:
            self.cursor.execute('SELECT subject_id, subject_name, table_name FROM subjects ORDER BY subject_name')
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Ошибка получения предметов: {e}")
    
    def get_subject_by_id(self, subject_id: int) -> Optional[Dict[str, Any]]:
        """
        Получение предмета по ID.
        
        Args:
            subject_id: ID предмета
            
        Returns:
            Словарь с информацией о предмете или None
        """
        try:
            self.cursor.execute(
                'SELECT subject_id, subject_name, table_name FROM subjects WHERE subject_id = ?',
                (subject_id,)
            )
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            raise Exception(f"Ошибка получения предмета: {e}")
    
    def delete_subject(self, subject_id: int) -> Tuple[bool, str]:
        """
        Удаление предмета и всех связанных данных.
        
        Args:
            subject_id: ID предмета
            
        Returns:
            Кортеж (успех, сообщение)
        """
        try:
            # Получаем информацию о предмете
            subject = self.get_subject_by_id(subject_id)
            if not subject:
                return False, "Предмет не найден"
            
            # Удаляем таблицу вопросов
            self.cursor.execute(f"DROP TABLE IF EXISTS {subject['table_name']}")
            
            # Удаляем результаты тестирования по этому предмету
            self.cursor.execute('DELETE FROM results WHERE subject_id = ?', (subject_id,))
            
            # Удаляем предмет
            self.cursor.execute('DELETE FROM subjects WHERE subject_id = ?', (subject_id,))
            
            self.conn.commit()
            return True, f"Предмет '{subject['subject_name']}' успешно удалён"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Ошибка удаления предмета: {e}"
    
    # ==================== Методы работы с учащимися ====================
    
    def add_student(self, first_name: str, last_name: str, group_name: str, 
                    birth_date: str, patronymic: Optional[str] = None) -> Tuple[bool, str]:
        """
        Добавление нового учащегося.
        
        Args:
            first_name: Имя учащегося
            last_name: Фамилия учащегося
            group_name: Название группы
            birth_date: Дата рождения (формат ГГГГ-ММ-ДД)
            patronymic: Отчество (необязательно)
            
        Returns:
            Кортеж (успех, сообщение)
        """
        if not first_name or not first_name.strip():
            return False, "Имя не может быть пустым"
        if not last_name or not last_name.strip():
            return False, "Фамилия не может быть пустой"
        if not group_name or not group_name.strip():
            return False, "Группа не может быть пустой"
        if not birth_date or not birth_date.strip():
            return False, "Дата рождения не может быть пустой"
        
        # Валидация даты с проверкой реалистичности
        validation_result = self.validate_birth_date(birth_date.strip())
        if not validation_result[0]:
            return False, validation_result[1]
        
        try:
            self.cursor.execute('''
                INSERT INTO students (first_name, last_name, patronymic, group_name, birth_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (first_name.strip(), last_name.strip(), patronymic.strip() if patronymic else None,
                  group_name.strip(), birth_date.strip()))
            
            self.conn.commit()
            return True, f"Студент {last_name.strip()} {first_name.strip()} успешно добавлен"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Ошибка добавления студента: {e}"
    
    def validate_birth_date(self, birth_date: str) -> Tuple[bool, str]:
        """
        Валидация даты рождения на реалистичность.
        
        Args:
            birth_date: Дата рождения в формате ГГГГ-ММ-ДД
            
        Returns:
            Кортеж (успех, сообщение)
        """
        try:
            date_obj = datetime.strptime(birth_date, '%Y-%m-%d')
        except ValueError:
            return False, "Неверный формат даты. Используйте ГГГГ-ММ-ДД"
        
        year = date_obj.year
        month = date_obj.month
        day = date_obj.day
        
        # Проверка диапазона года (1900-2026)
        if year < 1900 or year > 2026:
            return False, f"Год должен быть в диапазоне от 1900 до 2026 (указан: {year})"
        
        # Проверка диапазона месяца (01-12)
        if month < 1 or month > 12:
            return False, f"Месяц должен быть в диапазоне от 01 до 12 (указан: {month})"
        
        # Проверка дня в зависимости от месяца
        days_in_month = {
            1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
            7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
        }
        
        # Проверка високосного года для февраля
        if month == 2:
            is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
            max_day = 29 if is_leap else 28
        else:
            max_day = days_in_month[month]
        
        if day < 1 or day > max_day:
            return False, f"День должен быть в диапазоне от 01 до {max_day} для месяца {month} (указан: {day})"
        
        return True, "Дата корректна"
    
    def get_student(self, student_id: int) -> Optional[Dict[str, Any]]:
        """
        Получение информации об учащемся по ID.
        
        Args:
            student_id: ID учащегося
            
        Returns:
            Словарь с информацией об учащемся или None
        """
        try:
            self.cursor.execute('''
                SELECT student_id, first_name, last_name, patronymic, group_name, birth_date
                FROM students WHERE student_id = ?
            ''', (student_id,))
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            raise Exception(f"Ошибка получения студента: {e}")
    
    def get_all_students(self) -> List[Dict[str, Any]]:
        """
        Получение списка всех учащихся.
        
        Returns:
            Список словарей с информацией об учащихся
        """
        try:
            self.cursor.execute('''
                SELECT student_id, first_name, last_name, patronymic, group_name, birth_date
                FROM students ORDER BY last_name, first_name
            ''')
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Ошибка получения студентов: {e}")
    
    def search_students_by_name(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Поиск учащихся по фамилии или имени (регистронезависимый).
        
        Args:
            search_term: Поисковый запрос
            
        Returns:
            Список найденных учащихся
        """
        try:
            # Приводим поисковый запрос к нижнему регистру для регистронезависимого поиска
            search_term_lower = search_term.strip().lower()
            search_pattern = f"%{search_term_lower}%"
            self.cursor.execute('''
                SELECT student_id, first_name, last_name, patronymic, group_name, birth_date
                FROM students 
                WHERE LOWER(last_name) LIKE ? OR LOWER(first_name) LIKE ? OR 
                      (LOWER(patronymic) LIKE ? AND patronymic IS NOT NULL)
                ORDER BY last_name, first_name
            ''', (search_pattern, search_pattern, search_pattern))
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Ошибка поиска студентов: {e}")
    
    def delete_student(self, student_id: int) -> Tuple[bool, str]:
        """
        Удаление учащегося и всех его результатов.
        
        Args:
            student_id: ID учащегося
            
        Returns:
            Кортеж (успех, сообщение)
        """
        try:
            student = self.get_student(student_id)
            if not student:
                return False, "Студент не найден"
            
            # Удаляем все результаты студента
            self.cursor.execute('DELETE FROM results WHERE student_id = ?', (student_id,))
            
            # Удаляем студента
            self.cursor.execute('DELETE FROM students WHERE student_id = ?', (student_id,))
            
            self.conn.commit()
            return True, f"Студент {student['last_name']} {student['first_name']} успешно удалён"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Ошибка удаления студента: {e}"
    
    # ==================== Методы работы с вопросами ====================
    
    def add_question(self, subject_id: int, question_text: str, 
                     variant_a: str, variant_b: str, variant_c: str, variant_d: str,
                     correct_answer: str, question_number: Optional[int] = None) -> Tuple[bool, str]:
        """
        Добавление нового вопроса к предмету.
        
        Args:
            subject_id: ID предмета
            question_text: Текст вопроса
            variant_a: Вариант ответа A
            variant_b: Вариант ответа B
            variant_c: Вариант ответа C
            variant_d: Вариант ответа D
            correct_answer: Правильный ответ ('A', 'B', 'C' или 'D')
            question_number: Номер вопроса (необязательно, автоинкремент если не указан)
            
        Returns:
            Кортеж (успех, сообщение)
        """
        if not question_text or not question_text.strip():
            return False, "Текст вопроса не может быть пустым"
        if correct_answer not in ['A', 'B', 'C', 'D']:
            return False, "Правильный ответ должен быть A, B, C или D"
        
        subject = self.get_subject_by_id(subject_id)
        if not subject:
            return False, "Предмет не найден"
        
        table_name = subject['table_name']
        
        # Если номер вопроса не указан, получаем следующий доступный
        if question_number is None:
            self.cursor.execute(f'SELECT MAX(question_number) FROM {table_name}')
            result = self.cursor.fetchone()
            question_number = (result[0] or 0) + 1
        
        try:
            self.cursor.execute(f'''
                INSERT INTO {table_name} 
                (question_number, question_text, variant_a, variant_b, variant_c, variant_d, correct_answer)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (question_number, question_text.strip(), variant_a.strip(), variant_b.strip(),
                  variant_c.strip(), variant_d.strip(), correct_answer))
            
            self.conn.commit()
            return True, f"Вопрос №{question_number} успешно добавлен"
        except sqlite3.IntegrityError:
            return False, f"Вопрос с номером {question_number} уже существует"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Ошибка добавления вопроса: {e}"
    
    def get_questions_by_subject(self, subject_id: int) -> List[Dict[str, Any]]:
        """
        Получение всех вопросов для предмета.
        
        Args:
            subject_id: ID предмета
            
        Returns:
            Список словарей с вопросами
        """
        subject = self.get_subject_by_id(subject_id)
        if not subject:
            return []
        
        table_name = subject['table_name']
        
        try:
            self.cursor.execute(f'''
                SELECT question_id, question_number, question_text, variant_a, variant_b,
                       variant_c, variant_d, correct_answer
                FROM {table_name} ORDER BY question_number
            ''')
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Ошибка получения вопросов: {e}")
    
    def get_question_by_id(self, subject_id: int, question_id: int) -> Optional[Dict[str, Any]]:
        """
        Получение вопроса по ID.
        
        Args:
            subject_id: ID предмета
            question_id: ID вопроса
            
        Returns:
            Словарь с информацией о вопросе или None
        """
        subject = self.get_subject_by_id(subject_id)
        if not subject:
            return None
        
        table_name = subject['table_name']
        
        try:
            self.cursor.execute(f'''
                SELECT question_id, question_number, question_text, variant_a, variant_b,
                       variant_c, variant_d, correct_answer
                FROM {table_name} WHERE question_id = ?
            ''', (question_id,))
            row = self.cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            raise Exception(f"Ошибка получения вопроса: {e}")
    
    def delete_question(self, subject_id: int, question_id: int) -> Tuple[bool, str]:
        """
        Удаление вопроса.
        
        Args:
            subject_id: ID предмета
            question_id: ID вопроса
            
        Returns:
            Кортеж (успех, сообщение)
        """
        subject = self.get_subject_by_id(subject_id)
        if not subject:
            return False, "Предмет не найден"
        
        table_name = subject['table_name']
        
        try:
            self.cursor.execute(f'DELETE FROM {table_name} WHERE question_id = ?', (question_id,))
            
            if self.cursor.rowcount == 0:
                return False, "Вопрос не найден"
            
            self.conn.commit()
            return True, "Вопрос успешно удалён"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Ошибка удаления вопроса: {e}"
    
    def update_question(self, subject_id: int, question_id: int, question_number: int,
                        question_text: str, variant_a: str, variant_b: str, 
                        variant_c: str, variant_d: str, correct_answer: str) -> Tuple[bool, str]:
        """
        Обновление вопроса.
        
        Args:
            subject_id: ID предмета
            question_id: ID вопроса
            question_number: Номер вопроса
            question_text: Текст вопроса
            variant_a: Вариант ответа A
            variant_b: Вариант ответа B
            variant_c: Вариант ответа C
            variant_d: Вариант ответа D
            correct_answer: Правильный ответ ('A', 'B', 'C' или 'D')
            
        Returns:
            Кортеж (успех, сообщение)
        """
        if not question_text or not question_text.strip():
            return False, "Текст вопроса не может быть пустым"
        if correct_answer not in ['A', 'B', 'C', 'D']:
            return False, "Правильный ответ должен быть A, B, C или D"
        
        subject = self.get_subject_by_id(subject_id)
        if not subject:
            return False, "Предмет не найден"
        
        table_name = subject['table_name']
        
        try:
            self.cursor.execute(f'''
                UPDATE {table_name}
                SET question_number = ?, question_text = ?, variant_a = ?, variant_b = ?,
                    variant_c = ?, variant_d = ?, correct_answer = ?
                WHERE question_id = ?
            ''', (question_number, question_text.strip(), variant_a.strip(), variant_b.strip(),
                  variant_c.strip(), variant_d.strip(), correct_answer, question_id))
            
            if self.cursor.rowcount == 0:
                return False, "Вопрос не найден"
            
            self.conn.commit()
            return True, "Вопрос успешно обновлён"
        except sqlite3.IntegrityError:
            return False, f"Вопрос с номером {question_number} уже существует"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Ошибка обновления вопроса: {e}"
    
    # ==================== Методы работы с результатами ====================
    
    def save_result(self, student_id: int, subject_id: int, 
                    score: int, total_questions: int) -> Tuple[bool, str]:
        """
        Сохранение результата тестирования.
        
        Args:
            student_id: ID учащегося
            subject_id: ID предмета
            score: Количество правильных ответов
            total_questions: Общее количество вопросов
            
        Returns:
            Кортеж (успех, сообщение)
        """
        if total_questions <= 0:
            return False, "Общее количество вопросов должно быть больше 0"
        if score < 0 or score > total_questions:
            return False, "Некорректное количество баллов"
        
        percentage = round((score / total_questions) * 100, 2)
        
        try:
            self.cursor.execute('''
                INSERT INTO results (student_id, subject_id, score, total_questions, percentage)
                VALUES (?, ?, ?, ?, ?)
            ''', (student_id, subject_id, score, total_questions, percentage))
            
            self.conn.commit()
            return True, f"Результат сохранён: {score}/{total_questions} ({percentage}%)"
        except sqlite3.Error as e:
            self.conn.rollback()
            return False, f"Ошибка сохранения результата: {e}"
    
    def get_results_by_student(self, student_id: int) -> List[Dict[str, Any]]:
        """
        Получение всех результатов тестирования для учащегося.
        
        Args:
            student_id: ID учащегося
            
        Returns:
            Список словарей с результатами (включая ФИО студента)
        """
        try:
            self.cursor.execute('''
                SELECT r.result_id, r.student_id, st.last_name, st.first_name, st.patronymic,
                       r.subject_id, s.subject_name,
                       r.score, r.total_questions, r.percentage, r.test_date
                FROM results r
                JOIN subjects s ON r.subject_id = s.subject_id
                JOIN students st ON r.student_id = st.student_id
                WHERE r.student_id = ?
                ORDER BY r.test_date DESC
            ''', (student_id,))
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Ошибка получения результатов: {e}")
    
    def get_results_by_subject(self, subject_id: int) -> List[Dict[str, Any]]:
        """
        Получение всех результатов тестирования для предмета.
        
        Args:
            subject_id: ID предмета
            
        Returns:
            Список словарей с результатами
        """
        try:
            self.cursor.execute('''
                SELECT r.result_id, r.student_id, st.last_name, st.first_name, st.patronymic,
                       r.subject_id, su.subject_name, r.score, r.total_questions, 
                       r.percentage, r.test_date
                FROM results r
                JOIN students st ON r.student_id = st.student_id
                JOIN subjects su ON r.subject_id = su.subject_id
                WHERE r.subject_id = ?
                ORDER BY r.test_date DESC
            ''', (subject_id,))
            rows = self.cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            raise Exception(f"Ошибка получения результатов: {e}")
    
    def has_student_taken_test(self, student_id: int, subject_id: int) -> bool:
        """
        Проверка, проходил ли студент тест по предмету.
        
        Args:
            student_id: ID учащегося
            subject_id: ID предмета
            
        Returns:
            True если тест уже проходил, иначе False
        """
        try:
            self.cursor.execute('''
                SELECT COUNT(*) FROM results 
                WHERE student_id = ? AND subject_id = ?
            ''', (student_id, subject_id))
            result = self.cursor.fetchone()
            return result[0] > 0
        except sqlite3.Error as e:
            raise Exception(f"Ошибка проверки результата: {e}")
    
    def get_statistics_by_subject(self, subject_id: int) -> Dict[str, Any]:
        """
        Получение статистики по предмету.
        
        Args:
            subject_id: ID предмета
            
        Returns:
            Словарь со статистикой
        """
        try:
            self.cursor.execute('''
                SELECT 
                    COUNT(*) as total_tests,
                    AVG(percentage) as avg_percentage,
                    MIN(percentage) as min_percentage,
                    MAX(percentage) as max_percentage
                FROM results
                WHERE subject_id = ?
            ''', (subject_id,))
            row = self.cursor.fetchone()
            
            if row and row['total_tests'] > 0:
                return {
                    'total_tests': row['total_tests'],
                    'avg_percentage': round(row['avg_percentage'], 2) if row['avg_percentage'] else 0,
                    'min_percentage': round(row['min_percentage'], 2) if row['min_percentage'] else 0,
                    'max_percentage': round(row['max_percentage'], 2) if row['max_percentage'] else 0
                }
            return {
                'total_tests': 0,
                'avg_percentage': 0,
                'min_percentage': 0,
                'max_percentage': 0
            }
        except sqlite3.Error as e:
            raise Exception(f"Ошибка получения статистики: {e}")
    
    def close(self):
        """Закрытие соединения с базой данных."""
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        """Деструктор класса."""
        self.close()
