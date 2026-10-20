import unittest
from src.core.calculator import Calculator

class TestCalculator(unittest.TestCase):
    def test_basic_arithmetic(self):
        res = Calculator.calculate("12 + 34 * 2")
        self.assertIsNotNone(res)
        self.assertEqual(res["target"], "80")

    def test_power(self):
        res = Calculator.calculate("2^10")
        self.assertIsNotNone(res)
        self.assertEqual(res["target"], "1024")

    def test_math_functions(self):
        res = Calculator.calculate("sqrt(144)")
        self.assertIsNotNone(res)
        self.assertEqual(res["target"], "12")

    def test_percentage(self):
        res = Calculator.calculate("15% of 200")
        self.assertIsNotNone(res)
        self.assertEqual(res["target"], "30")

    def test_equal_prefix(self):
        res = Calculator.calculate("= 100 / 4")
        self.assertIsNotNone(res)
        self.assertEqual(res["target"], "25")

    def test_invalid_string(self):
        res = Calculator.calculate("chrome.exe")
        self.assertIsNone(res)

        res2 = Calculator.calculate("notepad")
        self.assertIsNone(res2)

if __name__ == "__main__":
    unittest.main()
