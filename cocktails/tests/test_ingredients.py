"""Integration tests for the ingredient endpoints."""

from cocktails.models import Ingredient

from .base import BaseTestCase


class IngredientListTests(BaseTestCase):
    def test_list_empty(self):
        response = self.client.get("/api/ingredients/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"items": [], "total": 0, "page": 1, "pages": 1})

    def test_list_paginated(self):
        for i in range(15):
            Ingredient.objects.create(name=f"Ingredient {i}")
        response = self.client.get("/api/ingredients/", {"per_page": 10})
        data = response.json()
        self.assertEqual(data["total"], 15)
        self.assertEqual(len(data["items"]), 10)
        self.assertEqual(data["page"], 1)
        self.assertEqual(data["pages"], 2)

    def test_list_second_page(self):
        for i in range(15):
            Ingredient.objects.create(name=f"Ingredient {i}")
        response = self.client.get("/api/ingredients/", {"page": 2, "per_page": 10})
        data = response.json()
        self.assertEqual(data["page"], 2)
        self.assertEqual(len(data["items"]), 5)


class IngredientCreateTests(BaseTestCase):
    def test_create_requires_authentication(self):
        response = self.post_json(
            "/api/ingredients/",
            {"name": "Mint", "description": "Fresh mint", "is_alcoholic": False},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json()["error"], "You must be logged in to add an ingredient."
        )

    def test_create(self):
        self.create_user("alice")
        self.login()
        response = self.post_json(
            "/api/ingredients/",
            {"name": "Mint", "description": "Fresh mint", "is_alcoholic": False},
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["name"], "Mint")
        self.assertEqual(data["description"], "Fresh mint")
        self.assertFalse(data["is_alcoholic"])
        self.assertTrue(Ingredient.objects.filter(name="Mint").exists())

    def test_create_defaults(self):
        self.create_user("alice")
        self.login()
        response = self.post_json("/api/ingredients/", {"name": "Soda"})
        self.assertEqual(response.status_code, 201)
        ingredient = Ingredient.objects.get(name="Soda")
        self.assertEqual(ingredient.description, "")
        self.assertFalse(ingredient.is_alcoholic)

    def test_create_missing_name(self):
        self.create_user("alice")
        self.login()
        response = self.post_json("/api/ingredients/", {"description": "no name"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "The 'name' field is required.")

    def test_create_invalid_json(self):
        self.create_user("alice")
        self.login()
        response = self.client.post(
            "/api/ingredients/", data="not-json", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Invalid JSON format.")


class IngredientDetailTests(BaseTestCase):
    def setUp(self):
        self.ingredient = self.create_ingredient("Mint", "Fresh mint", False)

    def test_retrieve(self):
        response = self.client.get(f"/api/ingredients/{self.ingredient.id}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Mint")
        self.assertEqual(data["image"], None)

    def test_retrieve_not_found(self):
        response = self.client.get("/api/ingredients/9999/")
        self.assertEqual(response.status_code, 404)

    def test_update_requires_auth(self):
        response = self.put_json(
            f"/api/ingredients/{self.ingredient.id}/",
            {"name": "Spearmint"},
        )
        self.assertEqual(response.status_code, 401)

    def test_update_forbidden_for_non_admin(self):
        self.create_user("bob")
        self.login("bob")
        response = self.put_json(
            f"/api/ingredients/{self.ingredient.id}/",
            {"name": "Spearmint"},
        )
        self.assertEqual(response.status_code, 403)

    def test_update(self):
        self.create_admin("admin")
        self.login("admin")
        response = self.put_json(
            f"/api/ingredients/{self.ingredient.id}/",
            {"name": "Spearmint", "is_alcoholic": True},
        )
        self.assertEqual(response.status_code, 200)
        self.ingredient.refresh_from_db()
        self.assertEqual(self.ingredient.name, "Spearmint")
        self.assertTrue(self.ingredient.is_alcoholic)

    def test_update_not_found(self):
        response = self.put_json("/api/ingredients/9999/", {"name": "X"})
        self.assertEqual(response.status_code, 404)

    def test_update_invalid_json(self):
        self.create_admin("admin")
        self.login("admin")
        response = self.client.put(
            f"/api/ingredients/{self.ingredient.id}/",
            data="not-json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Invalid JSON format.")

    def test_delete_requires_auth(self):
        response = self.client.delete(f"/api/ingredients/{self.ingredient.id}/")
        self.assertEqual(response.status_code, 401)

    def test_delete_forbidden_for_non_admin(self):
        self.create_user("bob")
        self.login("bob")
        response = self.client.delete(f"/api/ingredients/{self.ingredient.id}/")
        self.assertEqual(response.status_code, 403)

    def test_delete(self):
        self.create_admin("admin")
        self.login("admin")
        response = self.client.delete(f"/api/ingredients/{self.ingredient.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Ingredient.objects.filter(id=self.ingredient.id).exists())

    def test_delete_not_found(self):
        response = self.client.delete("/api/ingredients/9999/")
        self.assertEqual(response.status_code, 404)
