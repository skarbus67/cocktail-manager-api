"""Tests for pagination parameter validation."""

from .base import BaseTestCase


class PaginationValidationTests(BaseTestCase):
    # --- non-numeric input -------------------------------------------------

    def test_ingredient_list_rejects_non_numeric_per_page(self):
        response = self.client.get("/api/ingredients/", {"per_page": "abc"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("integers", response.json()["error"])

    def test_ingredient_list_rejects_non_numeric_page(self):
        response = self.client.get("/api/ingredients/", {"page": "abc"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("integers", response.json()["error"])

    def test_cocktail_list_rejects_non_numeric_per_page(self):
        response = self.client.get("/api/cocktails/", {"per_page": "abc"})
        self.assertEqual(response.status_code, 400)

    def test_cocktail_list_rejects_non_numeric_page(self):
        response = self.client.get("/api/cocktails/", {"page": "abc"})
        self.assertEqual(response.status_code, 400)

    def test_review_list_rejects_non_numeric_per_page(self):
        cocktail = self.create_cocktail("Mojito")
        response = self.client.get(
            f"/api/cocktails/{cocktail.id}/reviews/", {"per_page": "abc"}
        )
        self.assertEqual(response.status_code, 400)

    # --- non-positive input ------------------------------------------------

    def test_ingredient_list_rejects_zero_per_page(self):
        response = self.client.get("/api/ingredients/", {"per_page": "0"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("positive", response.json()["error"])

    def test_ingredient_list_rejects_negative_page(self):
        response = self.client.get("/api/ingredients/", {"page": "-1"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("positive", response.json()["error"])

    # --- valid input -------------------------------------------------------

    def test_ingredient_list_accepts_valid_pagination(self):
        for i in range(3):
            self.create_ingredient(f"Ingredient {i}")
        response = self.client.get("/api/ingredients/", {"page": 1, "per_page": 2})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["page"], 1)
        self.assertEqual(len(data["items"]), 2)
