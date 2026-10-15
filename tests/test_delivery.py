import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from delivery import calculate_delivery_cost


class TestDelivery(unittest.TestCase):

    # ========== Успешные базовые случаи ==========

    def test_normal_small_package(self):
        cost, date = calculate_delivery_cost(1.0, 100, "обычный", False)
        self.assertIsInstance(cost, int)
        self.assertGreater(cost, 0)
        self.assertRegex(date, r"\d{4}-\d{2}-\d{2}")

    def test_fragile_package_adds_surcharge(self):
        cost_normal, _ = calculate_delivery_cost(2.0, 200, "обычный", False)
        cost_fragile, _ = calculate_delivery_cost(2.0, 200, "хрупкий", False)
        self.assertEqual(cost_fragile, cost_normal + 300)

    def test_dangerous_package_adds_surcharge(self):
        cost_normal, _ = calculate_delivery_cost(2.0, 200, "обычный", False)
        cost_danger, _ = calculate_delivery_cost(2.0, 200, "опасный", False)
        self.assertEqual(cost_danger, cost_normal + 1000)

    # ========== Весовые коэффициенты ==========

    def test_weight_between_5_and_20_applies_1_2(self):
        cost_light, _ = calculate_delivery_cost(4.0, 100, "обычный", False)
        cost_medium, _ = calculate_delivery_cost(10.0, 100, "обычный", False)
        self.assertAlmostEqual(cost_medium, int(cost_light * 1.2))

    def test_weight_20_and_more_applies_1_5(self):
        cost_light, _ = calculate_delivery_cost(4.0, 100, "обычный", False)
        cost_heavy, _ = calculate_delivery_cost(25.0, 100, "обычный", False)
        self.assertAlmostEqual(cost_heavy, int(cost_light * 1.5))

    # ========== Экспресс (здесь ожидаем падения) ==========

    def test_express_should_be_more_expensive(self):
        """Экспресс должен стоить дороже, а не дешевле"""
        cost_normal, _ = calculate_delivery_cost(3.0, 300, "обычный", False)
        cost_express, _ = calculate_delivery_cost(3.0, 300, "обычный", True)
        self.assertGreater(cost_express, cost_normal)

    def test_express_reduces_delivery_days(self):
        _, date_normal = calculate_delivery_cost(2.0, 1200, "обычный", False)
        _, date_express = calculate_delivery_cost(2.0, 1200, "обычный", True)
        self.assertNotEqual(date_normal, date_express)

    # ========== Граничные и невалидные значения ==========

    def test_weight_too_small(self):
        cost, date = calculate_delivery_cost(0.05, 100, "обычный", False)
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_weight_too_big(self):
        cost, date = calculate_delivery_cost(51.0, 100, "обычный", False)
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_distance_too_small(self):
        cost, date = calculate_delivery_cost(1.0, 0, "обычный", False)
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_distance_too_big(self):
        cost, date = calculate_delivery_cost(1.0, 5001, "обычный", False)
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_invalid_package_type(self):
        cost, date = calculate_delivery_cost(1.0, 100, "неизвестный", False)
        self.assertEqual(cost, -1)
        self.assertEqual(date, "0000-00-00")

    def test_valid_boundary_weight_0_1(self):
        cost, date = calculate_delivery_cost(0.1, 100, "обычный", False)
        self.assertNotEqual(cost, -1)

    def test_valid_boundary_weight_50(self):
        cost, date = calculate_delivery_cost(50.0, 100, "обычный", False)
        self.assertNotEqual(cost, -1)

    def test_valid_boundary_distance_1(self):
        cost, date = calculate_delivery_cost(1.0, 1, "обычный", False)
        self.assertNotEqual(cost, -1)

    def test_valid_boundary_distance_5000(self):
        cost, date = calculate_delivery_cost(1.0, 5000, "обычный", False)
        self.assertNotEqual(cost, -1)


if __name__ == "__main__":
    unittest.main()