"""
Точка входа в приложение системы контроля знаний учащихся.
Запускает графический интерфейс приложения.
"""

from app_ui import KnowledgeControlApp
import tkinter as tk


def main():
    """
    Основная функция запуска приложения.
    Создаёт главное окно и инициализирует приложение.
    """
    # Создание главного окна
    root = tk.Tk()
    
    # Настройка окна
    root.title("Система контроля знаний учащихся")
    root.geometry("1200x800")
    root.minsize(900, 600)
    
    # Иконка окна (если доступна)
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    # Создание экземпляра приложения
    app = KnowledgeControlApp(root)
    
    # Обработчик закрытия окна
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Запуск главного цикла обработки событий
    root.mainloop()


if __name__ == "__main__":
    main()
