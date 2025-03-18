import unittest
from ExpenseManagerLib import ExpenseManagerLib

class TestExpenseManager(unittest.TestCase):
    def setUp(self):
        self.manager = ExpenseManagerLib()

    def test_categorize_expense_food(self):
        result = self.manager.categorize_expense("Dinner at restaurant")
        self.assertEqual(result, "food")

    def test_categorize_expense_transport(self):
        result = self.manager.categorize_expense("Uber ride to airport")
        self.assertEqual(result, "transport")

    def test_categorize_expense_default(self):
        result = self.manager.categorize_expense("Bought new shoes")
        self.assertEqual(result, "others")

if __name__ == '__main__':
    unittest.main()
