import unittest

from duckfine import DuckFine


class TestDuckFineInit(unittest.TestCase):
    def test_stores_member_id(self):
        fine = DuckFine("M001")
        self.assertEqual(fine.member_id, "M001")

    def test_total_owed_starts_at_zero(self):
        fine = DuckFine("M001")
        self.assertEqual(fine.total_owed, 0.0)


class TestDuckFineCharge(unittest.TestCase):
    def setUp(self):
        self.fine = DuckFine("M001")

    # --- invalid input ---

    def test_negative_days_raises_value_error(self):
        with self.assertRaises(ValueError):
            self.fine.charge(-1)

    def test_negative_days_does_not_change_total_owed(self):
        with self.assertRaises(ValueError):
            self.fine.charge(-1)
        self.assertEqual(self.fine.total_owed, 0.0)

    # --- grace period ---

    def test_zero_days_late_is_free(self):
        self.assertEqual(self.fine.charge(0), 0.0)

    def test_last_grace_day_is_free(self):
        self.assertEqual(self.fine.charge(DuckFine.GRACE_DAYS), 0.0)

    def test_first_day_after_grace_charges_one_daily_fee(self):
        self.assertAlmostEqual(self.fine.charge(3), 0.50)

    # --- standard fee ---

    def test_fee_is_daily_fee_times_chargeable_days(self):
        self.assertAlmostEqual(self.fine.charge(6), 2.00)

    def test_fee_just_below_cap_is_not_capped(self):
        self.assertAlmostEqual(self.fine.charge(11), 4.50)

    def test_fee_exactly_at_cap(self):
        self.assertAlmostEqual(self.fine.charge(12), 5.00)

    def test_fee_above_cap_is_capped(self):
        self.assertAlmostEqual(self.fine.charge(30), DuckFine.MAX_FEE)

    # --- deluxe ---

    def test_deluxe_doubles_fee(self):
        self.assertAlmostEqual(self.fine.charge(4, deluxe=True), 2.00)

    def test_deluxe_within_grace_is_free(self):
        self.assertEqual(self.fine.charge(2, deluxe=True), 0.0)

    def test_deluxe_fee_exactly_at_cap(self):
        self.assertAlmostEqual(self.fine.charge(7, deluxe=True), 5.00)

    def test_deluxe_fee_is_capped_after_doubling(self):
        self.assertAlmostEqual(self.fine.charge(8, deluxe=True), DuckFine.MAX_FEE)

    def test_deluxe_defaults_to_false(self):
        self.assertAlmostEqual(self.fine.charge(4), 1.00)

    # --- running total ---

    def test_charge_adds_fee_to_total_owed(self):
        self.fine.charge(4)
        self.assertAlmostEqual(self.fine.total_owed, 1.00)

    def test_total_owed_accumulates_across_charges(self):
        self.fine.charge(4)
        self.fine.charge(5, deluxe=True)
        self.assertAlmostEqual(self.fine.total_owed, 4.00)

    def test_total_owed_can_exceed_single_fine_cap(self):
        self.fine.charge(30)
        self.fine.charge(30)
        self.assertAlmostEqual(self.fine.total_owed, 10.00)

    def test_free_charge_leaves_total_owed_unchanged(self):
        self.fine.charge(4)
        self.fine.charge(1)
        self.assertAlmostEqual(self.fine.total_owed, 1.00)

    def test_separate_members_have_independent_totals(self):
        other = DuckFine("M002")
        self.fine.charge(4)
        self.assertEqual(other.total_owed, 0.0)


if __name__ == "__main__":
    unittest.main()
