"""Integration tests for cocktail filtering, sorting and pagination."""

from .base import BaseTestCase


class CocktailFilteringTests(BaseTestCase):
    def setUp(self):
        self.mint = self.create_ingredient("Mint", is_alcoholic=False)
        self.rum = self.create_ingredient("Rum", is_alcoholic=True)
        self.soda = self.create_ingredient("Soda", is_alcoholic=False)

        self.alice = self.create_user("alice")
        self.bob = self.create_user("bob")

        # Non-alcoholic: mint + soda
        self.virgin_mojito = self.create_cocktail(
            "Virgin Mojito", category="Mocktail", author=self.alice,
            ingredients=[(self.mint, "10 g"), (self.soda, "100 ml")],
        )
        # Alcoholic: mint + rum
        self.classic_mojito = self.create_cocktail(
            "Classic Mojito", category="Classic", author=self.alice,
            ingredients=[(self.mint, "10 g"), (self.rum, "50 ml")],
        )
        # Alcoholic: rum only
        self.rum_cola = self.create_cocktail(
            "Rum Cola", category="Long Drink", author=self.bob,
            ingredients=[(self.rum, "50 ml")],
        )

    def get_names(self, **params):
        response = self.client.get("/api/cocktails/", params)
        self.assertEqual(response.status_code, 200)
        return [item["name"] for item in response.json()["items"]]

    def test_default_order_is_by_id(self):
        self.assertEqual(
            self.get_names(), ["Virgin Mojito", "Classic Mojito", "Rum Cola"]
        )

    def test_sort_by_name(self):
        self.assertEqual(
            self.get_names(sort="name"),
            ["Classic Mojito", "Rum Cola", "Virgin Mojito"],
        )

    def test_sort_by_name_descending(self):
        self.assertEqual(
            self.get_names(sort="-name"),
            ["Virgin Mojito", "Rum Cola", "Classic Mojito"],
        )

    def test_sort_by_category(self):
        self.assertEqual(
            self.get_names(sort="category"),
            ["Classic Mojito", "Rum Cola", "Virgin Mojito"],
        )

    def test_invalid_sort_falls_back_to_id(self):
        self.assertEqual(
            self.get_names(sort="unsafe"),
            ["Virgin Mojito", "Classic Mojito", "Rum Cola"],
        )

    def test_filter_by_author(self):
        self.assertEqual(
            self.get_names(author_id=self.alice.id),
            ["Virgin Mojito", "Classic Mojito"],
        )

    def test_filter_by_ingredient_name(self):
        self.assertEqual(
            self.get_names(ingredient="mint"),
            ["Virgin Mojito", "Classic Mojito"],
        )

    def test_filter_non_alcoholic(self):
        self.assertEqual(self.get_names(is_alcoholic="false"), ["Virgin Mojito"])

    def test_filter_alcoholic(self):
        self.assertEqual(
            self.get_names(is_alcoholic="true"),
            ["Classic Mojito", "Rum Cola"],
        )

    def test_combined_non_alcoholic_with_mint(self):
        self.assertEqual(
            self.get_names(ingredient="mint", is_alcoholic="false"),
            ["Virgin Mojito"],
        )

    def test_pagination_per_page(self):
        response = self.client.get("/api/cocktails/", {"per_page": 2})
        data = response.json()
        self.assertEqual(data["total"], 3)
        self.assertEqual(len(data["items"]), 2)
        self.assertEqual(data["pages"], 2)
        self.assertEqual(data["page"], 1)
