import unittest

from energy_logic import calculate_energy_financials


class TestEnergyFinancials(unittest.TestCase):
    """Unit tests for calculate_energy_financials."""

    def test_empty_devices_list(self):
        """Empty list should return (0.0, 0.0, 0.0)."""
        result = calculate_energy_financials([])

        self.assertEqual(result, (0.0, 0.0, 0.0))

    def test_financials_with_discount(self):
        """Total consumption >= 50,000 kWh should apply 3% discount."""
        devices_list = [
            {
                "id": "M01",
                "location": "Shop A",
                "old_index": 0,
                "new_index": 30000,
                "status": "Normal",
            },
            {
                "id": "M02",
                "location": "Shop B",
                "old_index": 0,
                "new_index": 25000,
                "status": "Normal",
            },
        ]

        total_kwh, discount_percent, final_cost = calculate_energy_financials(
            devices_list
        )

        expected_base_cost = 55000 * 3000
        expected_final_cost = expected_base_cost * 0.97

        self.assertEqual(total_kwh, 55000)
        self.assertEqual(discount_percent, 3.0)
        self.assertEqual(final_cost, expected_final_cost)

    def test_financials_no_discount(self):
        """Total consumption below 50,000 kWh should have 0% discount."""
        devices_list = [
            {
                "id": "M01",
                "location": "Shop A",
                "old_index": 1000,
                "new_index": 15000,
                "status": "Normal",
            },
            {
                "id": "M02",
                "location": "Shop B",
                "old_index": 500,
                "new_index": 20000,
                "status": "Normal",
            },
        ]

        total_kwh, discount_percent, final_cost = calculate_energy_financials(
            devices_list
        )

        expected_total_kwh = (15000 - 1000) + (20000 - 500)
        expected_final_cost = expected_total_kwh * 3000

        self.assertEqual(total_kwh, expected_total_kwh)
        self.assertEqual(discount_percent, 0.0)
        self.assertEqual(final_cost, expected_final_cost)


if __name__ == "__main__":
    unittest.main()
