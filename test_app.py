import unittest

from app import app


class TestHealth(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_health_returns_ok(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})


class TestFine(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    # a. fee comes back as JSON with the right value

    def test_fee_returned_as_json(self):
        response = self.client.get("/fine?days=6")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)
        self.assertAlmostEqual(response.get_json()["fee"], 2.00)

    def test_fee_within_grace_period_is_zero(self):
        response = self.client.get("/fine?days=2")
        self.assertEqual(response.get_json()["fee"], 0.0)

    def test_fee_is_capped(self):
        response = self.client.get("/fine?days=30")
        self.assertAlmostEqual(response.get_json()["fee"], 5.00)

    # b. deluxe flag reaches the calculation

    def test_deluxe_doubles_fee(self):
        standard = self.client.get("/fine?days=4").get_json()["fee"]
        deluxe = self.client.get("/fine?days=4&deluxe=1").get_json()["fee"]
        self.assertAlmostEqual(standard, 1.00)
        self.assertAlmostEqual(deluxe, 2.00)

    def test_deluxe_zero_is_standard(self):
        response = self.client.get("/fine?days=4&deluxe=0")
        self.assertAlmostEqual(response.get_json()["fee"], 1.00)

    # c. non-numeric days give 400

    def test_non_numeric_days_returns_400(self):
        response = self.client.get("/fine?days=abc")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_decimal_days_returns_400(self):
        response = self.client.get("/fine?days=2.5")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_missing_days_returns_400(self):
        response = self.client.get("/fine")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    # d. negative days give 400

    def test_negative_days_returns_400(self):
        response = self.client.get("/fine?days=-1")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())


if __name__ == "__main__":
    unittest.main()
