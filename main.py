# Personal Finance Tracker
# Проект для отслеживания личных финансов
# Автор: [mkrugley]
# Дата: 2025

import json
import os
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
    
    def __init__(self, data_file: str = 'transactions.json'):
        self.data_file = data_file
        self.transactions: List[Transaction] = []
        self.load_data()
    
    def load_data(self):
        """Загрузка данных из файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Преобразуем словари обратно в объекты Transaction
                    self.transactions = [
                        Transaction.from_dict(t) for t in data
                    ]
                print(f"Загружено {len(self.transactions)} транзакций")
            except Exception as e:
                print(f"Ошибка при загрузке данных: {e}")
                self.transactions = []
        else:
            print("Файл данных не найден, создаём новый")
            self.transactions = []
    
    def save_data(self):
        """Сохранение данных в файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                # Конвертируем объекты в словари для JSON
                data = [t.to_dict() for t in self.transactions]
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("Данные успешно сохранены")
        except Exception as e:
            print(f"Ошибка при сохранении: {e}")
    
    def add_transaction(self, amount: float, category: str, 
                       description: str) -> bool:
        """Добавление новой транзакции"""
        try:
            transaction = Transaction(amount, category, description)
            self.transactions.append(transaction)
            self.save_data()
            print(f"Транзакция добавлена: {amount} руб. ({category})")
            return True
        except Exception as e:
            print(f"Ошибка при добавлении транзакции: {e}")
            return False
    
    def get_balance(self) -> float:
        """Расчёт текущего баланса"""
        balance = sum(t.amount for t in self.transactions)
        return balance
    
    def get_transactions_by_category(self, category: str) -> List[Transaction]:
        """Получение всех транзакций по категории"""
        return [t for t in self.transactions if t.category == category]
    
    def get_category_totals(self) -> Dict[str, float]:
        """Получение суммы по каждой категории"""
        totals = {}
        for transaction in self.transactions:
            category = transaction.category
            if category not in totals:
                totals[category] = 0
            totals[category] += transaction.amount
        return totals
    
    def delete_transaction(self, index: int) -> bool:
        """Удаление транзакции по индексу"""
        try:
            if 0 <= index < len(self.transactions):
                deleted = self.transactions.pop(index)
                self.save_data()
                print(f"Удалена транзакция: {deleted.description}")
                return True
            else:
                print("Неверный индекс транзакции")
                return False
        except Exception as e:
            print(f"Ошибка при удалении: {e}")
            return False

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
    
    # Разделяем на доходы и расходы
    income = sum(t.amount for t in tracker.transactions if t.amount > 0)
    expenses = sum(t.amount for t in tracker.transactions if t.amount < 0)
    
    print(f"💰 Баланс: {balance:.2f} руб.")
    print(f"📈 Доходы: {income:.2f} руб.")
    print(f"📉 Расходы: {expenses:.2f} руб.")
    print()

def show_all_transactions(tracker: FinanceTracker):
    """Показать все транзакции"""
    print_header("Все транзакции")
    
    if not tracker.transactions:
        print("📭 Транзакций пока нет")
        return
    
    # Сортируем по дате (новые первые)
    sorted_transactions = sorted(
        tracker.transactions, 
        key=lambda x: x.date, 
        reverse=True
    )
    
    for i, transaction in enumerate(sorted_transactions):
        sign = "+" if transaction.amount > 0 else ""
        print(f"{i+1}. [{transaction.date}] "
              f"{transaction.category}: {transaction.description}")
        print(f"   {sign}{transaction.amount:.2f} руб.\n")

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
    
    if not tracker.transactions:
        print("📭 Транзакций пока нет")
        return
    
    # Показываем все транзакции с номерами
    for i, transaction in enumerate(tracker.transactions):
        sign = "+" if transaction.amount > 0 else ""
        print(f"{i+1}. [{transaction.date}] "
              f"{transaction.category}: {transaction.description} - "
              f"{sign}{transaction.amount:.2f} руб.")
    
    print()
    try:
        choice = int(input("Введите номер транзакции для удаления (0 - отмена): "))
        if choice == 0:
            return
        
        if tracker.delete_transaction(choice - 1):
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
