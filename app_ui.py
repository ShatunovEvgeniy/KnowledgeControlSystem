"""
Модуль графического интерфейса системы контроля знаний.
Содержит класс KnowledgeControlApp для создания GUI на базе Tkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Optional, Dict, Any, List
from knowledgecontrol import KnowledgeControlSystem


class KnowledgeControlApp:
    """
    Класс графического интерфейса приложения контроля знаний.
    Создаёт главное окно с вкладками для управления предметами,
    учащимися и проведения тестирования.
    """
    
    def __init__(self, root: tk.Tk):
        """
        Инициализация приложения.
        
        Args:
            root: Корневой элемент Tkinter
        """
        self.root = root
        self.root.title("Система контроля знаний учащихся")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)
        
        # Инициализация системы работы с данными
        self.system = KnowledgeControlSystem()
        
        # Переменные для хранения текущего состояния
        self.current_subject_id: Optional[int] = None
        self.current_student_id: Optional[int] = None
        self.test_questions: List[Dict[str, Any]] = []
        self.selected_answers: Dict[int, str] = {}
        
        # Создание виджетов
        self.create_widgets()
        
        # Загрузка начальных данных
        self.update_subjects_list()
        self.update_students_list()
    
    def create_widgets(self):
        """Создание основных виджетов приложения."""
        # Создание стильной панели вкладок
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#f0f0f0')
        style.configure('TNotebook.Tab', padding=[20, 10], font=('Arial', 11, 'bold'))
        style.configure('TButton', padding=[10, 5], font=('Arial', 10))
        style.configure('TLabel', font=('Arial', 10))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Success.TLabel', foreground='green', font=('Arial', 10, 'bold'))
        style.configure('Error.TLabel', foreground='red', font=('Arial', 10, 'bold'))
        
        # Создание контейнера вкладок
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Вкладка 1: Предметы и вопросы
        self.subjects_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.subjects_tab, text="📚 Предметы и вопросы")
        self.setup_subjects_tab()
        
        # Вкладка 2: Учащиеся и результаты
        self.students_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.students_tab, text="👨‍🎓 Учащиеся и результаты")
        self.setup_students_tab()
        
        # Вкладка 3: Проведение тестирования
        self.testing_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.testing_tab, text="✏️ Проведение тестирования")
        self.setup_testing_tab()
    
    # ==================== Вкладка 1: Предметы и вопросы ====================
    
    def setup_subjects_tab(self):
        """Настройка вкладки предметов и вопросов."""
        # Левая панель - список предметов
        left_frame = ttk.LabelFrame(self.subjects_tab, text="Предметы", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Форма добавления предмета
        add_subject_frame = ttk.LabelFrame(left_frame, text="Добавление предмета", padding=10)
        add_subject_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(add_subject_frame, text="Название предмета:").pack(anchor=tk.W)
        self.subject_name_entry = ttk.Entry(add_subject_frame, width=40)
        self.subject_name_entry.pack(fill=tk.X, pady=(5, 10))
        
        ttk.Button(add_subject_frame, text="➕ Добавить предмет", 
                   command=self.add_subject).pack()
        
        # Список предметов
        ttk.Label(left_frame, text="Список предметов:", style='Header.TLabel').pack(anchor=tk.W)
        
        columns = ('ID', 'Название', 'Таблица')
        self.subjects_tree = ttk.Treeview(left_frame, columns=columns, show='headings', height=10)
        self.subjects_tree.heading('ID', text='ID')
        self.subjects_tree.heading('Название', text='Название предмета')
        self.subjects_tree.heading('Таблица', text='Таблица вопросов')
        self.subjects_tree.column('ID', width=50)
        self.subjects_tree.column('Название', width=200)
        self.subjects_tree.column('Таблица', width=150)
        self.subjects_tree.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        self.subjects_tree.bind('<<TreeviewSelect>>', self.on_subject_select)
        
        # Кнопка удаления предмета
        ttk.Button(left_frame, text="🗑️ Удалить предмет", 
                   command=self.delete_subject).pack(pady=5)
        
        # Правая панель - вопросы
        right_frame = ttk.LabelFrame(self.subjects_tab, text="Вопросы", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Форма добавления вопроса
        add_question_frame = ttk.LabelFrame(right_frame, text="Добавление вопроса", padding=10)
        add_question_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Номер вопроса
        ttk.Label(add_question_frame, text="Номер вопроса:").grid(row=0, column=0, sticky=tk.W)
        self.question_number_entry = ttk.Entry(add_question_frame, width=10)
        self.question_number_entry.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        # Текст вопроса
        ttk.Label(add_question_frame, text="Текст вопроса:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.question_text_entry = ttk.Entry(add_question_frame, width=40)
        self.question_text_entry.grid(row=1, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        
        # Варианты ответов
        ttk.Label(add_question_frame, text="Вариант A:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.variant_a_entry = ttk.Entry(add_question_frame, width=30)
        self.variant_a_entry.grid(row=2, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(add_question_frame, text="Вариант B:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.variant_b_entry = ttk.Entry(add_question_frame, width=30)
        self.variant_b_entry.grid(row=3, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(add_question_frame, text="Вариант C:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.variant_c_entry = ttk.Entry(add_question_frame, width=30)
        self.variant_c_entry.grid(row=4, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(add_question_frame, text="Вариант D:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.variant_d_entry = ttk.Entry(add_question_frame, width=30)
        self.variant_d_entry.grid(row=5, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        
        # Правильный ответ
        ttk.Label(add_question_frame, text="Правильный ответ:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.correct_answer_var = tk.StringVar(value="A")
        answer_frame = ttk.Frame(add_question_frame)
        answer_frame.grid(row=6, column=1, columnspan=3, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(answer_frame, text="A", variable=self.correct_answer_var, 
                        value="A").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(answer_frame, text="B", variable=self.correct_answer_var, 
                        value="B").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(answer_frame, text="C", variable=self.correct_answer_var, 
                        value="C").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(answer_frame, text="D", variable=self.correct_answer_var, 
                        value="D").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(add_question_frame, text="➕ Добавить вопрос", 
                   command=self.add_question).grid(row=7, column=0, columnspan=4, pady=10)
        
        # Список вопросов
        ttk.Label(right_frame, text="Список вопросов:", style='Header.TLabel').pack(anchor=tk.W)
        
        q_columns = ('№', 'Вопрос', 'Ответ')
        self.questions_tree = ttk.Treeview(right_frame, columns=q_columns, show='headings', height=8)
        self.questions_tree.heading('№', text='№')
        self.questions_tree.heading('Вопрос', text='Текст вопроса')
        self.questions_tree.heading('Ответ', text='Правильный')
        self.questions_tree.column('№', width=40)
        self.questions_tree.column('Вопрос', width=300)
        self.questions_tree.column('Ответ', width=80)
        self.questions_tree.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        self.questions_tree.bind('<<TreeviewSelect>>', self.on_question_select)
        
        # Кнопка удаления вопроса
        ttk.Button(right_frame, text="🗑️ Удалить вопрос", 
                   command=self.delete_question).pack(pady=5)
        
        # Статус бар
        self.subject_status_label = ttk.Label(self.subjects_tab, text="", style='Success.TLabel')
        self.subject_status_label.pack(fill=tk.X, padx=10, pady=5)
    
    def update_subjects_list(self):
        """Обновление списка предметов в таблице."""
        # Очистка таблицы
        for item in self.subjects_tree.get_children():
            self.subjects_tree.delete(item)
        
        # Заполнение данными
        subjects = self.system.get_all_subjects()
        for subject in subjects:
            self.subjects_tree.insert('', tk.END, values=(
                subject['subject_id'],
                subject['subject_name'],
                subject['table_name']
            ))
    
    def update_questions_list(self):
        """Обновление списка вопросов для выбранного предмета."""
        # Очистка таблицы
        for item in self.questions_tree.get_children():
            self.questions_tree.delete(item)
        
        if self.current_subject_id is None:
            return
        
        # Заполнение данными
        questions = self.system.get_questions_by_subject(self.current_subject_id)
        for question in questions:
            # Обрезаем текст вопроса для отображения
            question_text = question['question_text'][:50] + "..." if len(question['question_text']) > 50 else question['question_text']
            self.questions_tree.insert('', tk.END, values=(
                question['question_number'],
                question_text,
                question['correct_answer']
            ))
    
    def on_subject_select(self, event):
        """Обработчик выбора предмета."""
        selection = self.subjects_tree.selection()
        if selection:
            item = self.subjects_tree.item(selection[0])
            self.current_subject_id = item['values'][0]
            self.update_questions_list()
    
    def on_question_select(self, event):
        """Обработчик выбора вопроса для редактирования."""
        selection = self.questions_tree.selection()
        if not selection or self.current_subject_id is None:
            return
        
        item = self.questions_tree.item(selection[0])
        question_number = item['values'][0]
        
        # Находим ID вопроса и полные данные
        questions = self.system.get_questions_by_subject(self.current_subject_id)
        selected_question = None
        for q in questions:
            if q['question_number'] == question_number:
                selected_question = q
                break
        
        if selected_question is None:
            return
        
        # Открываем диалог редактирования
        self.edit_question_dialog(selected_question)
    
    def edit_question_dialog(self, question: Dict[str, Any]):
        """Диалоговое окно редактирования вопроса."""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Редактирование вопроса №{question['question_number']}")
        dialog.geometry("700x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Форма редактирования
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Номер вопроса
        ttk.Label(main_frame, text="Номер вопроса:").grid(row=0, column=0, sticky=tk.W, pady=5)
        question_number_entry = ttk.Entry(main_frame, width=10)
        question_number_entry.grid(row=0, column=1, sticky=tk.W, padx=5)
        question_number_entry.insert(0, str(question['question_number']))
        
        # Текст вопроса
        ttk.Label(main_frame, text="Текст вопроса:").grid(row=1, column=0, sticky=tk.W, pady=5)
        question_text_entry = ttk.Entry(main_frame, width=50)
        question_text_entry.grid(row=1, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        question_text_entry.insert(0, question['question_text'])
        
        # Варианты ответов
        ttk.Label(main_frame, text="Вариант A:").grid(row=2, column=0, sticky=tk.W, pady=5)
        variant_a_entry = ttk.Entry(main_frame, width=40)
        variant_a_entry.grid(row=2, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        variant_a_entry.insert(0, question['variant_a'])
        
        ttk.Label(main_frame, text="Вариант B:").grid(row=3, column=0, sticky=tk.W, pady=5)
        variant_b_entry = ttk.Entry(main_frame, width=40)
        variant_b_entry.grid(row=3, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        variant_b_entry.insert(0, question['variant_b'])
        
        ttk.Label(main_frame, text="Вариант C:").grid(row=4, column=0, sticky=tk.W, pady=5)
        variant_c_entry = ttk.Entry(main_frame, width=40)
        variant_c_entry.grid(row=4, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        variant_c_entry.insert(0, question['variant_c'])
        
        ttk.Label(main_frame, text="Вариант D:").grid(row=5, column=0, sticky=tk.W, pady=5)
        variant_d_entry = ttk.Entry(main_frame, width=40)
        variant_d_entry.grid(row=5, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=5)
        variant_d_entry.insert(0, question['variant_d'])
        
        # Правильный ответ
        ttk.Label(main_frame, text="Правильный ответ:").grid(row=6, column=0, sticky=tk.W, pady=5)
        correct_answer_var = tk.StringVar(value=question['correct_answer'])
        answer_frame = ttk.Frame(main_frame)
        answer_frame.grid(row=6, column=1, columnspan=3, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(answer_frame, text="A", variable=correct_answer_var, value="A").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(answer_frame, text="B", variable=correct_answer_var, value="B").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(answer_frame, text="C", variable=correct_answer_var, value="C").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(answer_frame, text="D", variable=correct_answer_var, value="D").pack(side=tk.LEFT, padx=5)
        
        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=7, column=0, columnspan=4, pady=20)
        
        def save_changes():
            try:
                new_number = int(question_number_entry.get().strip())
            except ValueError:
                messagebox.showerror("Ошибка", "Номер вопроса должен быть числом!")
                return
            
            success, message = self.system.update_question(
                self.current_subject_id,
                question['question_id'],
                new_number,
                question_text_entry.get().strip(),
                variant_a_entry.get().strip(),
                variant_b_entry.get().strip(),
                variant_c_entry.get().strip(),
                variant_d_entry.get().strip(),
                correct_answer_var.get()
            )
            
            if success:
                messagebox.showinfo("Успех", message)
                self.update_questions_list()
                dialog.destroy()
            else:
                messagebox.showerror("Ошибка", message)
        
        ttk.Button(btn_frame, text="💾 Сохранить изменения", command=save_changes).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="❌ Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=10)
        
        # Конфигурация колонок
        main_frame.columnconfigure(1, weight=1)
    
    def add_subject(self):
        """Добавление нового предмета."""
        subject_name = self.subject_name_entry.get().strip()
        
        if not subject_name:
            messagebox.showwarning("Предупреждение", "Введите название предмета!")
            return
        
        success, message = self.system.add_subject(subject_name)
        
        if success:
            self.subject_status_label.config(text=message, style='Success.TLabel')
            self.subject_name_entry.delete(0, tk.END)
            self.update_subjects_list()
            messagebox.showinfo("Успех", message)
        else:
            self.subject_status_label.config(text=message, style='Error.TLabel')
            messagebox.showerror("Ошибка", message)
    
    def delete_subject(self):
        """Удаление выбранного предмета."""
        selection = self.subjects_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите предмет для удаления!")
            return
        
        item = self.subjects_tree.item(selection[0])
        subject_id = item['values'][0]
        subject_name = item['values'][1]
        
        if messagebox.askyesno("Подтверждение", 
                               f"Вы уверены, что хотите удалить предмет '{subject_name}'?\n"
                               f"Все вопросы и результаты будут удалены!"):
            success, message = self.system.delete_subject(subject_id)
            
            if success:
                self.current_subject_id = None
                self.update_subjects_list()
                self.update_questions_list()
                messagebox.showinfo("Успех", message)
            else:
                messagebox.showerror("Ошибка", message)
    
    def add_question(self):
        """Добавление нового вопроса."""
        if self.current_subject_id is None:
            messagebox.showwarning("Предупреждение", "Выберите предмет для добавления вопроса!")
            return
        
        try:
            question_number = int(self.question_number_entry.get().strip()) if self.question_number_entry.get().strip() else None
        except ValueError:
            messagebox.showerror("Ошибка", "Номер вопроса должен быть числом!")
            return
        
        question_text = self.question_text_entry.get().strip()
        variant_a = self.variant_a_entry.get().strip()
        variant_b = self.variant_b_entry.get().strip()
        variant_c = self.variant_c_entry.get().strip()
        variant_d = self.variant_d_entry.get().strip()
        correct_answer = self.correct_answer_var.get()
        
        if not question_text:
            messagebox.showwarning("Предупреждение", "Введите текст вопроса!")
            return
        
        if not all([variant_a, variant_b, variant_c, variant_d]):
            messagebox.showwarning("Предупреждение", "Заполните все варианты ответов!")
            return
        
        success, message = self.system.add_question(
            self.current_subject_id, question_text,
            variant_a, variant_b, variant_c, variant_d,
            correct_answer, question_number
        )
        
        if success:
            self.subject_status_label.config(text=message, style='Success.TLabel')
            # Очистка полей
            self.question_number_entry.delete(0, tk.END)
            self.question_text_entry.delete(0, tk.END)
            self.variant_a_entry.delete(0, tk.END)
            self.variant_b_entry.delete(0, tk.END)
            self.variant_c_entry.delete(0, tk.END)
            self.variant_d_entry.delete(0, tk.END)
            self.correct_answer_var.set("A")
            self.update_questions_list()
            messagebox.showinfo("Успех", message)
        else:
            self.subject_status_label.config(text=message, style='Error.TLabel')
            messagebox.showerror("Ошибка", message)
    
    def delete_question(self):
        """Удаление выбранного вопроса."""
        if self.current_subject_id is None:
            messagebox.showwarning("Предупреждение", "Выберите предмет!")
            return
        
        selection = self.questions_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите вопрос для удаления!")
            return
        
        item = self.questions_tree.item(selection[0])
        question_number = item['values'][0]
        
        # Находим ID вопроса
        questions = self.system.get_questions_by_subject(self.current_subject_id)
        question_id = None
        for q in questions:
            if q['question_number'] == question_number:
                question_id = q['question_id']
                break
        
        if question_id is None:
            messagebox.showerror("Ошибка", "Вопрос не найден!")
            return
        
        if messagebox.askyesno("Подтверждение", 
                               f"Вы уверены, что хотите удалить вопрос №{question_number}?"):
            success, message = self.system.delete_question(self.current_subject_id, question_id)
            
            if success:
                self.update_questions_list()
                messagebox.showinfo("Успех", message)
            else:
                messagebox.showerror("Ошибка", message)
    
    # ==================== Вкладка 2: Учащиеся и результаты ====================
    
    def setup_students_tab(self):
        """Настройка вкладки учащихся и результатов."""
        # Верхняя часть - форма добавления студента и список
        top_frame = ttk.Frame(self.students_tab)
        top_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Левая панель - форма добавления
        left_frame = ttk.LabelFrame(top_frame, text="Добавление студента", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        ttk.Label(left_frame, text="Фамилия:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.student_last_name_entry = ttk.Entry(left_frame, width=25)
        self.student_last_name_entry.grid(row=0, column=1, pady=5)
        
        ttk.Label(left_frame, text="Имя:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.student_first_name_entry = ttk.Entry(left_frame, width=25)
        self.student_first_name_entry.grid(row=1, column=1, pady=5)
        
        ttk.Label(left_frame, text="Отчество:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.student_patronymic_entry = ttk.Entry(left_frame, width=25)
        self.student_patronymic_entry.grid(row=2, column=1, pady=5)
        
        ttk.Label(left_frame, text="Группа:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.student_group_entry = ttk.Entry(left_frame, width=25)
        self.student_group_entry.grid(row=3, column=1, pady=5)
        
        ttk.Label(left_frame, text="Дата рождения (ГГГГ-ММ-ДД):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.student_birth_date_entry = ttk.Entry(left_frame, width=25)
        self.student_birth_date_entry.grid(row=4, column=1, pady=5)
        
        ttk.Button(left_frame, text="➕ Добавить студента", 
                   command=self.add_student).grid(row=5, column=0, columnspan=2, pady=10)
        
        # Правая панель - список студентов
        right_frame = ttk.LabelFrame(top_frame, text="Список студентов", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Поиск
        search_frame = ttk.Frame(right_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="Поиск по фамилии:").pack(side=tk.LEFT)
        self.search_student_entry = ttk.Entry(search_frame, width=30)
        self.search_student_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="🔍 Найти", 
                   command=self.search_results_by_student).pack(side=tk.LEFT)
        ttk.Button(search_frame, text="🔄 Сброс", 
                   command=self.reset_search).pack(side=tk.LEFT, padx=5)
        
        # Таблица студентов
        s_columns = ('ID', 'Фамилия', 'Имя', 'Отчество', 'Группа', 'Дата рождения')
        self.students_tree = ttk.Treeview(right_frame, columns=s_columns, show='headings', height=10)
        self.students_tree.heading('ID', text='ID')
        self.students_tree.heading('Фамилия', text='Фамилия')
        self.students_tree.heading('Имя', text='Имя')
        self.students_tree.heading('Отчество', text='Отчество')
        self.students_tree.heading('Группа', text='Группа')
        self.students_tree.heading('Дата рождения', text='Дата рождения')
        self.students_tree.column('ID', width=40)
        self.students_tree.column('Фамилия', width=120)
        self.students_tree.column('Имя', width=100)
        self.students_tree.column('Отчество', width=120)
        self.students_tree.column('Группа', width=80)
        self.students_tree.column('Дата рождения', width=100)
        self.students_tree.pack(fill=tk.BOTH, expand=True)
        self.students_tree.bind('<<TreeviewSelect>>', self.on_student_select)
        
        # Нижняя часть - результаты
        bottom_frame = ttk.LabelFrame(self.students_tab, text="Результаты тестирования", padding=10)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        r_columns = ('Студент', 'Предмет', 'Баллы', 'Всего', 'Процент', 'Дата')
        self.results_tree = ttk.Treeview(bottom_frame, columns=r_columns, show='headings', height=8)
        self.results_tree.heading('Студент', text='ФИО студента')
        self.results_tree.heading('Предмет', text='Предмет')
        self.results_tree.heading('Баллы', text='Баллы')
        self.results_tree.heading('Всего', text='Всего вопросов')
        self.results_tree.heading('Процент', text='Процент')
        self.results_tree.heading('Дата', text='Дата теста')
        self.results_tree.column('Студент', width=200)
        self.results_tree.column('Предмет', width=150)
        self.results_tree.column('Баллы', width=60)
        self.results_tree.column('Всего', width=80)
        self.results_tree.column('Процент', width=80)
        self.results_tree.column('Дата', width=150)
        self.results_tree.pack(fill=tk.BOTH, expand=True)
        
        # Статус бар
        self.student_status_label = ttk.Label(self.students_tab, text="", style='Success.TLabel')
        self.student_status_label.pack(fill=tk.X, padx=10, pady=5)
    
    def update_students_list(self):
        """Обновление списка студентов."""
        for item in self.students_tree.get_children():
            self.students_tree.delete(item)
        
        students = self.system.get_all_students()
        for student in students:
            self.students_tree.insert('', tk.END, values=(
                student['student_id'],
                student['last_name'],
                student['first_name'],
                student['patronymic'] or '',
                student['group_name'],
                student['birth_date']
            ))
    
    def update_results_list(self, student_id: Optional[int] = None):
        """Обновление списка результатов."""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        if student_id is None:
            return
        
        # Получаем информацию о студенте для отображения
        student = self.system.get_student(student_id)
        student_name = ""
        if student:
            student_name = f"{student['last_name']} {student['first_name']} {student['patronymic'] or ''}".strip()
        
        results = self.system.get_results_by_student(student_id)
        for result in results:
            self.results_tree.insert('', tk.END, values=(
                student_name,  # Добавляем ФИО студента
                result['subject_name'],
                result['score'],
                result['total_questions'],
                f"{result['percentage']}%",
                result['test_date']
            ))
    
    def on_student_select(self, event):
        """Обработчик выбора студента."""
        selection = self.students_tree.selection()
        if selection:
            item = self.students_tree.item(selection[0])
            self.current_student_id = item['values'][0]
            self.update_results_list(self.current_student_id)
    
    def add_student(self):
        """Добавление нового студента."""
        last_name = self.student_last_name_entry.get().strip()
        first_name = self.student_first_name_entry.get().strip()
        patronymic = self.student_patronymic_entry.get().strip()
        group_name = self.student_group_entry.get().strip()
        birth_date = self.student_birth_date_entry.get().strip()
        
        if not all([last_name, first_name, group_name, birth_date]):
            messagebox.showwarning("Предупреждение", 
                                   "Заполните все обязательные поля!\n"
                                   "(Фамилия, Имя, Группа, Дата рождения)")
            return
        
        success, message = self.system.add_student(
            first_name, last_name, group_name, birth_date, patronymic
        )
        
        if success:
            self.student_status_label.config(text=message, style='Success.TLabel')
            # Очистка полей
            self.student_last_name_entry.delete(0, tk.END)
            self.student_first_name_entry.delete(0, tk.END)
            self.student_patronymic_entry.delete(0, tk.END)
            self.student_group_entry.delete(0, tk.END)
            self.student_birth_date_entry.delete(0, tk.END)
            self.update_students_list()
            messagebox.showinfo("Успех", message)
        else:
            self.student_status_label.config(text=message, style='Error.TLabel')
            messagebox.showerror("Ошибка", message)
    
    def search_results_by_student(self):
        """Поиск результатов по фамилии студента."""
        search_term = self.search_student_entry.get().strip()
        
        if not search_term:
            messagebox.showwarning("Предупреждение", "Введите фамилию для поиска!")
            return
        
        # Ищем студентов по фамилии
        students = self.system.search_students_by_name(search_term)
        
        if not students:
            messagebox.showinfo("Результат", f"Студенты с фамилией '{search_term}' не найдены")
            return
        
        # Если найден один студент - показываем его результаты
        if len(students) == 1:
            self.current_student_id = students[0]['student_id']
            self.update_results_list(self.current_student_id)
            messagebox.showinfo("Результат", f"Найден студент: {students[0]['last_name']} {students[0]['first_name']}")
        else:
            # Если несколько - выводим список
            result_text = f"Найдено студентов: {len(students)}\n\n"
            for student in students:
                result_text += f"- {student['last_name']} {student['first_name']} ({student['group_name']})\n"
            messagebox.showinfo("Результат поиска", result_text)
    
    def reset_search(self):
        """Сброс поиска."""
        self.search_student_entry.delete(0, tk.END)
        self.current_student_id = None
        self.update_results_list(None)
    
    # ==================== Вкладка 3: Проведение тестирования ====================
    
    def setup_testing_tab(self):
        """Настройка вкладки проведения тестирования."""
        # Верхняя часть - выбор студента и предмета
        top_frame = ttk.LabelFrame(self.testing_tab, text="Параметры тестирования", padding=10)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Выбор студента
        ttk.Label(top_frame, text="Выберите студента:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.test_student_combo = ttk.Combobox(top_frame, state='readonly', width=40)
        self.test_student_combo.grid(row=0, column=1, padx=10, pady=5)
        
        # Выбор предмета
        ttk.Label(top_frame, text="Выберите предмет:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.test_subject_combo = ttk.Combobox(top_frame, state='readonly', width=40)
        self.test_subject_combo.grid(row=1, column=1, padx=10, pady=5)
        
        # Кнопки управления
        btn_frame = ttk.Frame(top_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="🔄 Обновить списки", 
                   command=self.refresh_test_lists).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="▶️ Начать тестирование", 
                   command=self.start_test).pack(side=tk.LEFT, padx=5)
        
        # Область с вопросами
        middle_frame = ttk.LabelFrame(self.testing_tab, text="Вопросы теста", padding=10)
        middle_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Контейнер для скроллинга вопросов
        canvas = tk.Canvas(middle_frame)
        scrollbar = ttk.Scrollbar(middle_frame, orient="vertical", command=canvas.yview)
        self.questions_frame = ttk.Frame(canvas)
        
        self.questions_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.questions_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Нижняя часть - кнопки завершения
        bottom_frame = ttk.Frame(self.testing_tab)
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.test_info_label = ttk.Label(bottom_frame, text="", style='Header.TLabel')
        self.test_info_label.pack(side=tk.LEFT)
        
        ttk.Button(bottom_frame, text="💾 Завершить тестирование", 
                   command=self.save_result).pack(side=tk.RIGHT)
        
        # Статус бар
        self.test_status_label = ttk.Label(self.testing_tab, text="", style='Success.TLabel')
        self.test_status_label.pack(fill=tk.X, padx=10, pady=5)
    
    def refresh_test_lists(self):
        """Обновление списков студентов и предметов для тестирования."""
        # Обновление списка студентов
        students = self.system.get_all_students()
        student_values = [f"{s['last_name']} {s['first_name']} {s['patronymic'] or ''} ({s['group_name']}) - ID:{s['student_id']}" 
                          for s in students]
        self.test_student_combo['values'] = student_values
        
        # Обновление списка предметов
        subjects = self.system.get_all_subjects()
        subject_values = [f"{s['subject_name']} - ID:{s['subject_id']}" for s in subjects]
        self.test_subject_combo['values'] = subject_values
    
    def start_test(self):
        """Начало тестирования."""
        # Получение выбранных значений
        student_selection = self.test_student_combo.get()
        subject_selection = self.test_subject_combo.get()
        
        if not student_selection or not subject_selection:
            messagebox.showwarning("Предупреждение", "Выберите студента и предмет!")
            return
        
        # Извлечение ID
        try:
            self.current_student_id = int(student_selection.split("ID:")[-1])
            subject_id = int(subject_selection.split("ID:")[-1])
        except (ValueError, IndexError):
            messagebox.showerror("Ошибка", "Некорректный формат выбора!")
            return
        
        # Проверка, проходил ли студент этот тест
        if self.system.has_student_taken_test(self.current_student_id, subject_id):
            if not messagebox.askyesno("Предупреждение", 
                                       "Этот студент уже проходил тест по данному предмету!\n"
                                       "Продолжить?"):
                return
        
        # Загрузка вопросов
        self.test_questions = self.system.get_questions_by_subject(subject_id)
        
        if not self.test_questions:
            messagebox.showwarning("Предупреждение", "Для этого предмета нет вопросов!")
            return
        
        # Очистка предыдущих вопросов
        for widget in self.questions_frame.winfo_children():
            widget.destroy()
        
        self.selected_answers = {}
        
        # Создание виджетов для каждого вопроса
        for i, question in enumerate(self.test_questions):
            q_frame = ttk.LabelFrame(self.questions_frame, text=f"Вопрос {question['question_number']}", padding=10)
            q_frame.pack(fill=tk.X, pady=5, padx=5)
            
            # Текст вопроса
            ttk.Label(q_frame, text=question['question_text'], wraplength=800, 
                      style='Header.TLabel').pack(anchor=tk.W, pady=(0, 10))
            
            # Варианты ответов
            answer_var = tk.StringVar()
            self.selected_answers[question['question_id']] = answer_var
            
            ttk.Radiobutton(q_frame, text=f"A) {question['variant_a']}", 
                           variable=answer_var, value="A").pack(anchor=tk.W, pady=2)
            ttk.Radiobutton(q_frame, text=f"B) {question['variant_b']}", 
                           variable=answer_var, value="B").pack(anchor=tk.W, pady=2)
            ttk.Radiobutton(q_frame, text=f"C) {question['variant_c']}", 
                           variable=answer_var, value="C").pack(anchor=tk.W, pady=2)
            ttk.Radiobutton(q_frame, text=f"D) {question['variant_d']}", 
                           variable=answer_var, value="D").pack(anchor=tk.W, pady=2)
        
        # Обновление информации о тесте
        student = self.system.get_student(self.current_student_id)
        subject = self.system.get_subject_by_id(subject_id)
        self.test_info_label.config(
            text=f"Студент: {student['last_name']} {student['first_name']} | "
                 f"Предмет: {subject['subject_name']} | "
                 f"Вопросов: {len(self.test_questions)}"
        )
        
        self.test_status_label.config(text="Тестирование началось. Выберите ответы на вопросы.", 
                                      style='Success.TLabel')
    
    def save_result(self):
        """Сохранение результатов тестирования."""
        if not self.test_questions:
            messagebox.showwarning("Предупреждение", "Сначала начните тестирование!")
            return
        
        if self.current_student_id is None:
            messagebox.showwarning("Предупреждение", "Студент не выбран!")
            return
        
        # Подсчёт правильных ответов
        score = 0
        total = len(self.test_questions)
        
        for question in self.test_questions:
            selected = self.selected_answers.get(question['question_id'], '').get()
            if selected == question['correct_answer']:
                score += 1
        
        percentage = round((score / total) * 100, 2) if total > 0 else 0
        
        # Сохранение результата
        success, message = self.system.save_result(
            self.current_student_id,
            int(self.test_subject_combo.get().split("ID:")[-1]),
            score, total
        )
        
        if success:
            # Показ результата
            result_message = (f"Тестирование завершено!\n\n"
                              f"Правильных ответов: {score} из {total}\n"
                              f"Результат: {percentage}%\n\n")
            
            if percentage >= 90:
                result_message += "Оценка: Отлично! 🎉"
            elif percentage >= 75:
                result_message += "Оценка: Хорошо 👍"
            elif percentage >= 50:
                result_message += "Оценка: Удовлетворительно 👌"
            else:
                result_message += "Оценка: Неудовлетворительно 😞"
            
            self.test_status_label.config(text=f"Результат: {score}/{total} ({percentage}%)", 
                                          style='Success.TLabel')
            messagebox.showinfo("Результат тестирования", result_message)
            
            # Обновление результатов во вкладке студентов
            self.update_results_list(self.current_student_id)
        else:
            self.test_status_label.config(text=message, style='Error.TLabel')
            messagebox.showerror("Ошибка", message)
    
    def on_closing(self):
        """Обработчик закрытия приложения."""
        if messagebox.askokcancel("Выход", "Вы действительно хотите выйти?"):
            self.system.close()
            self.root.destroy()


def main():
    """Точка входа в приложение."""
    root = tk.Tk()
    app = KnowledgeControlApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
