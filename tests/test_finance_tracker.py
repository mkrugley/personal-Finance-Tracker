import unittest
import os
import tempfile
from main import FinanceTracker, Transaction

class TestTransaction(unittest.TestCase):
    def test_transaction_creation(self):
        """Test transaction creation with default date"""
        transaction = Transaction(100.0, "Salary", "Monthly salary")
        self.assertEqual(transaction.amount, 100.0)
        self.assertEqual(transaction.category, "Salary")
        self.assertEqual(transaction.description, "Monthly salary")
        self.assertIsNotNone(transaction.date)
    
    def test_transaction_creation_with_date(self):
        """Test transaction creation with specific date"""
        transaction = Transaction(100.0, "Salary", "Monthly salary", "2023-01-01")
        self.assertEqual(transaction.date, "2023-01-01")
    
    def test_transaction_to_dict(self):
        """Test conversion to dictionary"""
        transaction = Transaction(100.0, "Salary", "Monthly salary", "2023-01-01")
        data = transaction.to_dict()
        self.assertEqual(data['amount'], 100.0)
        self.assertEqual(data['category'], "Salary")
        self.assertEqual(data['description'], "Monthly salary")
        self.assertEqual(data['date'], "2023-01-01")
    
    def test_transaction_from_dict(self):
        """Test creation from dictionary"""
        data = {
            'amount': 100.0,
            'category': 'Salary',
            'description': 'Monthly salary',
            'date': '2023-01-01'
        }
        transaction = Transaction.from_dict(data)
        self.assertEqual(transaction.amount, 100.0)
        self.assertEqual(transaction.category, "Salary")
        self.assertEqual(transaction.description, "Monthly salary")
        self.assertEqual(transaction.date, "2023-01-01")

class TestFinanceTracker(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary database file for testing
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        self.tracker = FinanceTracker(self.test_db.name)
    
    def tearDown(self):
        """Tear down test fixtures after each test method."""
        # Clean up the temporary database file
        os.unlink(self.test_db.name)
    
    def test_init_db(self):
        """Test database initialization"""
        # Database should be initialized with transactions table
        transactions = self.tracker.get_all_transactions()
        self.assertIsInstance(transactions, list)
        self.assertEqual(len(transactions), 0)
    
    def test_add_transaction(self):
        """Test adding a transaction"""
        result = self.tracker.add_transaction(100.0, "Salary", "Monthly salary")
        self.assertTrue(result)
        
        transactions = self.tracker.get_all_transactions()
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]['amount'], 100.0)
        self.assertEqual(transactions[0]['category'], "Salary")
        self.assertEqual(transactions[0]['description'], "Monthly salary")
    
    def test_get_balance(self):
        """Test balance calculation"""
        # Add income
        self.tracker.add_transaction(100.0, "Salary", "Monthly salary")
        # Add expense
        self.tracker.add_transaction(-50.0, "Food", "Groceries")
        
        balance = self.tracker.get_balance()
        self.assertEqual(balance, 50.0)
    
    def test_get_transactions_by_category(self):
        """Test getting transactions by category"""
        # Add transactions
        self.tracker.add_transaction(100.0, "Salary", "Monthly salary")
        self.tracker.add_transaction(200.0, "Salary", "Bonus")
        self.tracker.add_transaction(-50.0, "Food", "Groceries")
        
        salary_transactions = self.tracker.get_transactions_by_category("Salary")
        self.assertEqual(len(salary_transactions), 2)
        self.assertEqual(salary_transactions[0]['amount'], 100.0)
        self.assertEqual(salary_transactions[1]['amount'], 200.0)
        
        food_transactions = self.tracker.get_transactions_by_category("Food")
        self.assertEqual(len(food_transactions), 1)
        self.assertEqual(food_transactions[0]['amount'], -50.0)
    
    def test_get_category_totals(self):
        """Test getting category totals"""
        # Add transactions
        self.tracker.add_transaction(100.0, "Salary", "Monthly salary")
        self.tracker.add_transaction(200.0, "Salary", "Bonus")
        self.tracker.add_transaction(-50.0, "Food", "Groceries")
        self.tracker.add_transaction(-30.0, "Food", "Restaurant")
        
        totals = self.tracker.get_category_totals()
        self.assertEqual(totals["Salary"], 300.0)
        self.assertEqual(totals["Food"], -80.0)
    
    def test_delete_transaction(self):
        """Test deleting a transaction"""
        # Add a transaction
        self.tracker.add_transaction(100.0, "Salary", "Monthly salary")
        transactions = self.tracker.get_all_transactions()
        transaction_id = transactions[0]['id']
        
        # Delete the transaction
        result = self.tracker.delete_transaction(transaction_id)
        self.assertTrue(result)
        
        # Verify it's deleted
        transactions = self.tracker.get_all_transactions()
        self.assertEqual(len(transactions), 0)
    
    def test_export_to_csv(self):
        """Test exporting to CSV"""
        # Add transactions
        self.tracker.add_transaction(100.0, "Salary", "Monthly salary")
        self.tracker.add_transaction(-50.0, "Food", "Groceries")
        
        # Export to CSV
        csv_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        csv_file.close()
        
        result = self.tracker.export_to_csv(csv_file.name)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(csv_file.name))
        
        # Clean up
        os.unlink(csv_file.name)
    
    def test_get_existing_categories(self):
        """Test getting existing categories"""
        # Add transactions
        self.tracker.add_transaction(100.0, "Salary", "Monthly salary")
        self.tracker.add_transaction(200.0, "Bonus", "Yearly bonus")
        self.tracker.add_transaction(-50.0, "Food", "Groceries")
        self.tracker.add_transaction(-30.0, "Transport", "Bus ticket")
        
        # Test income categories
        income_categories = self.tracker.get_existing_categories(income=True)
        self.assertIn("Salary", income_categories)
        self.assertIn("Bonus", income_categories)
        self.assertNotIn("Food", income_categories)
        
        # Test expense categories
        expense_categories = self.tracker.get_existing_categories(income=False)
        self.assertIn("Food", expense_categories)
        self.assertIn("Transport", expense_categories)
        self.assertNotIn("Salary", expense_categories)

if __name__ == '__main__':
    unittest.main()