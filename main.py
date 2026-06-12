# Personal Finance Tracker
# Проект для отслеживания личных финансов
# Автор: [mkrugley]
# Дата: 2025

import json
import os
import sqlite3
import csv
from datetime import datetime
from typing import List, Dict, Optional
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, FloatPrompt, IntPrompt
from rich.panel import Panel

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
    
    def export_to_csv(self, filename: str = 'transactions.csv') -> bool:
        """Экспорт всех транзакций в CSV файл"""
        try:
            transactions = self.get_all_transactions()
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['id', 'amount', 'category', 'description', 'date']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for transaction in transactions:
                    writer.writerow(transaction)
            
            print(f"✅ Данные экспортированы в {filename}")
            return True
        except Exception as e:
            print(f"❌ Ошибка при экспорте: {e}")
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
    console = Console()
    console.print(Panel(title, expand=False))

def print_menu():
    """Вывод главного меню"""
    console = Console()
    console.print("\n")
    console.print(Panel("💰 Personal Finance Tracker", expand=False))
    console.print("1. Добавить доход")
    console.print("2. Добавить расход")
    console.print("3. Показать баланс")
    console.print("4. Показать все транзакции")
    console.print("5. Статистика по категориям")
    console.print("6. Удалить транзакцию")
    console.print("7. Экспорт в CSV")
    console.print("0. Выход")
    console.print("\n")

def add_income(tracker: FinanceTracker):
    """Добавление дохода"""
    print_header("Добавить доход")
    
    try:
        amount = FloatPrompt.ask("Сумма")
        if amount <= 0:
            tracker.console.print("[red]❌ Сумма должна быть положительной[/red]")
            return
        
        tracker.console.print("\nКатегории дохода:")
        tracker.console.print("1. Зарплата")
        tracker.console.print("2. Фриланс")
        tracker.console.print("3. Инвестиции")
        tracker.console.print("4. Другое")
        
        choice = Prompt.ask("\nВыберите категорию (1-4)")
        categories = {
            '1': 'Зарплата',
            '2': 'Фриланс',
            '3': 'Инвестиции',
            '4': 'Другое'
        }
        
        category = categories.get(choice, 'Другое')
        description = Prompt.ask("Описание")
        
        if tracker.add_transaction(amount, category, description):
            tracker.console.print("[green]✅ Доход успешно добавлен![/green]")
        
    except ValueError:
        tracker.console.print("[red]❌ Неверный формат суммы[/red]")

def add_expense(tracker: FinanceTracker):
    """Добавление расхода"""
    print_header("Добавить расход")
    
    try:
        amount = FloatPrompt.ask("Сумма")
        if amount <= 0:
            tracker.console.print("[red]❌ Сумма должна быть положительной[/red]")
            return
        
        # Делаем сумму отрицательной для расхода
        amount = -amount
        
        tracker.console.print("\nКатегории расхода:")
        tracker.console.print("1. Еда")
        tracker.console.print("2. Транспорт")
        tracker.console.print("3. Развлечения")
        tracker.console.print("4. Здоровье")
        tracker.console.print("5. Образование")
        tracker.console.print("6. Другое")
        
        choice = Prompt.ask("\nВыберите категорию (1-6)")
        categories = {
            '1': 'Еда',
            '2': 'Транспорт',
            '3': 'Развлечения',
            '4': 'Здоровье',
            '5': 'Образование',
            '6': 'Другое'
        }
        
        category = categories.get(choice, 'Другое')
        description = Prompt.ask("Описание")
        
        if tracker.add_transaction(amount, category, description):
            tracker.console.print("[green]✅ Расход успешно добавлен![/green]")
        
    except ValueError:
        tracker.console.print("[red]❌ Неверный формат суммы[/red]")

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
    
    table = Table(show_header=False)
    table.add_column("Показатель", style="cyan")
    table.add_column("Значение", style="magenta")
    
    table.add_row("💰 Баланс", f"{balance:.2f} руб.")
    table.add_row("📈 Доходы", f"{income:.2f} руб.")
    table.add_row("📉 Расходы", f"{expenses:.2f} руб.")
    
    tracker.console.print(table)
    tracker.console.print("\n")

def show_all_transactions(tracker: FinanceTracker):
    """Показать все транзакции"""
    print_header("Все транзакции")
    
    transactions = tracker.get_all_transactions()
    
    if not transactions:
        tracker.console.print("[yellow]📭 Транзакций пока нет[/yellow]")
        return
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=5)
    table.add_column("Дата", style="dim")
    table.add_column("Категория")
    table.add_column("Описание")
    table.add_column("Сумма", justify="right")
    
    for transaction in transactions:
        sign = "+" if transaction['amount'] > 0 else ""
        amount_str = f"{sign}{transaction['amount']:.2f}"
        style = "green" if transaction['amount'] > 0 else "red"
        
        table.add_row(
            str(transaction['id']),
            transaction['date'],
            transaction['category'],
            transaction['description'],
            amount_str,
            style=style
        )
    
    tracker.console.print(table)
    tracker.console.print("\n")

def show_statistics(tracker: FinanceTracker):
    """Показать статистику по категориям"""
    print_header("Статистика по категориям")
    
    totals = tracker.get_category_totals()
    
    if not totals:
        tracker.console.print("[yellow]📭 Транзакций пока нет[/yellow]")
        return
    
    # Сортируем категории по сумме
    sorted_categories = sorted(
        totals.items(), 
        key=lambda x: abs(x[1]), 
        reverse=True
    )
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Категория", style="cyan")
    table.add_column("Сумма", justify="right")
    
    for category, amount in sorted_categories:
        sign = "+" if amount > 0 else ""
        amount_str = f"{sign}{amount:.2f}"
        style = "green" if amount > 0 else "red"
        
        table.add_row(category, amount_str, style=style)
    
    tracker.console.print(table)
    tracker.console.print("\n")

def delete_transaction_menu(tracker: FinanceTracker):
    """Меню удаления транзакции"""
    print_header("Удалить транзакцию")
    
    transactions = tracker.get_all_transactions()
    
    if not transactions:
        tracker.console.print("[yellow]📭 Транзакций пока нет[/yellow]")
        return
    
    # Показываем все транзакции с номерами
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="dim", width=5)
    table.add_column("Дата", style="dim")
    table.add_column("Категория")
    table.add_column("Описание")
    table.add_column("Сумма", justify="right")
    
    for transaction in transactions:
        sign = "+" if transaction['amount'] > 0 else ""
        amount_str = f"{sign}{transaction['amount']:.2f}"
        style = "green" if transaction['amount'] > 0 else "red"
        
        table.add_row(
            str(transaction['id']),
            transaction['date'],
            transaction['category'],
            transaction['description'],
            amount_str,
            style=style
        )
    
    tracker.console.print(table)
    
    try:
        choice = IntPrompt.ask("\nВведите ID транзакции для удаления (0 - отмена)")
        if choice == 0:
            return
        
        if tracker.delete_transaction(choice):
            tracker.console.print("[green]✅ Транзакция удалена![/green]")
        else:
            tracker.console.print("[red]❌ Не удалось удалить транзакцию[/red]")
            
    except ValueError:
        tracker.console.print("[red]❌ Неверный ввод[/red]")

def export_to_csv_menu(tracker: FinanceTracker):
    """Меню экспорта в CSV"""
    print_header("Экспорт в CSV")
    
    filename = Prompt.ask("Введите имя файла (по умолчанию transactions.csv)", default="transactions.csv")
    
    if not filename.endswith('.csv'):
        filename += '.csv'
    
    if tracker.export_to_csv(filename):
        tracker.console.print(f"[green]✅ Данные успешно экспортированы в {filename}[/green]")
    else:
        tracker.console.print("[red]❌ Ошибка при экспорте[/red]")

def main():
    """Главная функция программы"""
    tracker = FinanceTracker()
    console = Console()
    
    while True:
        print_menu()
        choice = Prompt.ask("Выберите действие", choices=['1', '2', '3', '4', '5', '6', '7', '0'])
        
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
        elif choice == '7':
            export_to_csv_menu(tracker)
        elif choice == '0':
            console.print("\n[bold cyan]👋 До свидания![/bold cyan]")
            break
        
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