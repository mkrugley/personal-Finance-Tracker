# Personal Finance Tracker
# Проект для отслеживания личных финансов
# Автор: [mkrugley]
# Дата: 2025

import json
import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class Transaction:
    """Класс для представления одной транзакции"""
    
    def __init__(self, amount: float, category: str, 
                 description: str, date: str = None):
        self.amount = amount
        self.category = category
        self.description = description
        # Если дата не указана, используем текущую
        if date is None:
            self.date = datetime.now().strftime("%Y-%m-%d")
        else:
            self.date = date
    
    def to_dict(self) -> Dict:
        """Конвертация транзакции в словарь для JSON"""
        return {
            'amount': self.amount,
            'category': self.category,
            'description': self.description,
            'date': self.date
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Создание транзакции из словаря"""
        return cls(
            amount=data['amount'],
            category=data['category'],
            description=data['description'],
            date=data['date']
        )

class FinanceTracker:
    """Основной класс для управления финансами"""
    
    def __init__(self, db_file: str = 'finance.db'):
        self.db_file = db_file
        self.init_db()
    
    def init_db(self):
        """Инициализация базы данных SQLite"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Создание таблицы транзакций
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                date TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_transaction(self, amount: float, category: str, 
                       description: str, date: str = None) -> bool:
        """Добавление новой транзакции"""
        try:
            if date is None:
                date = datetime.now().strftime("%Y-%m-%d")
            
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO transactions (amount, category, description, date)
                VALUES (?, ?, ?, ?)
            ''', (amount, category, description, date))
            
            conn.commit()
            conn.close()
            
            print(f"Транзакция добавлена: {amount} руб. ({category})")
            return True
        except Exception as e:
            print(f"Ошибка при добавлении транзакции: {e}")
            return False
    
    def get_balance(self) -> float:
        """Расчёт текущего баланса"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('SELECT SUM(amount) FROM transactions')
        result = cursor.fetchone()[0]
        
        conn.close()
        
        return result if result is not None else 0.0
    
    def get_transactions_by_category(self, category: str) -> List[Dict]:
        """Получение всех транзакций по категории"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT amount, category, description, date 
            FROM transactions 
            WHERE category = ?
        ''', (category,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{'amount': row[0], 'category': row[1], 'description': row[2], 'date': row[3]} 
                for row in rows]
    
    def get_category_totals(self) -> Dict[str, float]:
        """Получение суммы по каждой категории"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT category, SUM(amount) 
            FROM transactions 
            GROUP BY category
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return {row[0]: row[1] for row in rows}
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """Удаление транзакции по ID"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                print(f"Удалена транзакция с ID: {transaction_id}")
                return True
            else:
                conn.close()
                print("Транзакция с таким ID не найдена")
                return False
                
        except Exception as e:
            print(f"Ошибка при удалении: {e}")
            return False
    
    def get_all_transactions(self) -> List[Dict]:
        """Получение всех транзакций"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, amount, category, description, date 
            FROM transactions 
            ORDER BY date DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [{'id': row[0], 'amount': row[1], 'category': row[2], 'description': row[3], 'date': row[4]} 
                for row in rows]

def clear_screen():
    """Очистка экрана терминала"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title: str):
    """Красивый заголовок"""
    print("\n" + "="*50)
    print(f"  {title}")
    print("="*50 + "\n")

def print_menu():
    """Вывод главного меню"""
    print_header("💰 Personal Finance Tracker")
    print("1. Добавить доход")
    print("2. Добавить расход")
    print("3. Показать баланс")
    print("4. Показать все транзакции")
    print("5. Статистика по категориям")
    print("6. Удалить транзакцию")
    print("0. Выход")
    print()

def add_income(tracker: FinanceTracker):
    """Добавление дохода"""
    print_header("Добавить доход")
    
    try:
        amount = float(input("Сумма: "))
        if amount <= 0:
            print("❌ Сумма должна быть положительной")
            return
        
        print("\nКатегории дохода:")
        print("1. Зарплата")
        print("2. Фриланс")
        print("3. Инвестиции")
        print("4. Другое")
        
        choice = input("\nВыберите категорию (1-4): ")
        categories = {
            '1': 'Зарплата',
            '2': 'Фриланс',
            '3': 'Инвестиции',
            '4': 'Другое'
        }
        
        category = categories.get(choice, 'Другое')
        description = input("Описание: ")
        
        tracker.add_transaction(amount, category, description)
        print("✅ Доход успешно добавлен!")
        
    except ValueError:
        print("❌ Неверный формат суммы")

def add_expense(tracker: FinanceTracker):
    """Добавление расхода"""
    print_header("Добавить расход")
    
    try:
        amount = float(input("Сумма: "))
        if amount <= 0:
            print("❌ Сумма должна быть положительной")
            return
        
        # Делаем сумму отрицательной для расхода
        amount = -amount
        
        print("\nКатегории расхода:")
        print("1. Еда")
        print("2. Транспорт")
        print("3. Развлечения")
        print("4. Здоровье")
        print("5. Образование")
        print("6. Другое")
        
        choice = input("\nВыберите категорию (1-6): ")
        categories = {
            '1': 'Еда',
            '2': 'Транспорт',
            '3': 'Развлечения',
            '4': 'Здоровье',
            '5': 'Образование',
            '6': 'Другое'
        }
        
        category = categories.get(choice, 'Другое')
        description = input("Описание: ")
        
        tracker.add_transaction(amount, category, description)
        print("✅ Расход успешно добавлен!")
        
    except ValueError:
        print("❌ Неверный формат суммы")

def show_balance(tracker: FinanceTracker):
    """Показать текущий баланс"""
    print_header("Текущий баланс")
    
    balance = tracker.get_balance()
    
    # Получаем доходы и расходы отдельно
    conn = sqlite3.connect(tracker.db_file)
    cursor = conn.cursor()
    
    cursor.execute('SELECT SUM(amount) FROM transactions WHERE amount > 0')
    income = cursor.fetchone()[0] or 0.0
    
    cursor.execute('SELECT SUM(amount) FROM transactions WHERE amount < 0')
    expenses = cursor.fetchone()[0] or 0.0
    
    conn.close()
    
    print(f"💰 Баланс: {balance:.2f} руб.")
    print(f"📈 Доходы: {income:.2f} руб.")
    print(f"📉 Расходы: {expenses:.2f} руб.")
    print()

def show_all_transactions(tracker: FinanceTracker):
    """Показать все транзакции"""
    print_header("Все транзакции")
    
    transactions = tracker.get_all_transactions()
    
    if not transactions:
        print("📭 Транзакций пока нет")
        return
    
    for transaction in transactions:
        sign = "+" if transaction['amount'] > 0 else ""
        print(f"{transaction['id']}. [{transaction['date']}] "
              f"{transaction['category']}: {transaction['description']}")
        print(f"   {sign}{transaction['amount']:.2f} руб.\n")

def show_statistics(tracker: FinanceTracker):
    """Показать статистику по категориям"""
    print_header("Статистика по категориям")
    
    if not tracker.transactions:
        print("📭 Транзакций пока нет")
        return
    
    totals = tracker.get_category_totals()
    
    # Сортируем категории по сумме
    sorted_categories = sorted(
        totals.items(), 
        key=lambda x: abs(x[1]), 
        reverse=True
    )
    
    print("Категория              | Сумма")
    print("-" * 40)
    
    for category, amount in sorted_categories:
        sign = "+" if amount > 0 else ""
        print(f"{category:20} | {sign}{amount:.2f} руб.")
    
    print()

def delete_transaction_menu(tracker: FinanceTracker):
    """Меню удаления транзакции"""
    print_header("Удалить транзакцию")
    
    transactions = tracker.get_all_transactions()
    
    if not transactions:
        print("📭 Транзакций пока нет")
        return
    
    # Показываем все транзакции с номерами
    for transaction in transactions:
        sign = "+" if transaction['amount'] > 0 else ""
        print(f"{transaction['id']}. [{transaction['date']}] "
              f"{transaction['category']}: {transaction['description']} - "
              f"{sign}{transaction['amount']:.2f} руб.")
    
    print()
    try:
        choice = int(input("Введите ID транзакции для удаления (0 - отмена): "))
        if choice == 0:
            return
        
        if tracker.delete_transaction(choice):
            print("✅ Транзакция удалена!")
        else:
            print("❌ Не удалось удалить транзакцию")
            
    except ValueError:
        print("❌ Неверный ввод")

def main():
    """Главная функция программы"""
    tracker = FinanceTracker()
    
    while True:
        print_menu()
        choice = input("Выберите действие: ")
        
        if choice == '1':
            add_income(tracker)
        elif choice == '2':
            add_expense(tracker)
        elif choice == '3':
            show_balance(tracker)
        elif choice == '4':
            show_all_transactions(tracker)
        elif choice == '5':
            show_statistics(tracker)
        elif choice == '6':
            delete_transaction_menu(tracker)
        elif choice == '0':
            print("\n👋 До свидания!")
            break
        else:
            print("❌ Неверный выбор, попробуйте снова")
        
        # Пауза перед возвратом в меню
        input("\nНажмите Enter для продолжения...")
        clear_screen()

if __name__ == "__main__":
    # Запуск программы
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Программа остановлена пользователем")
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")