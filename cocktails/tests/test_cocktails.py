"""Integration tests for the cocktail endpoints and their authorization rules."""

from cocktails.models import Cocktail, CocktailIngredient

from .base import BaseTestCase


class CocktailCreateTests(BaseTestCase):
    def setUp(self):
        self.ingredient = self.create_ingredient("Mint")

    def test_create_requires_authentication(self):
        response = self.post_json(
            "/api/cocktails/",
            {"name": "Mojito", "category": "Classic", "instructions": "Shake."},
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json()["error"], "You must be logged in to add a recipe."
        )

    def test_create_requires_required_fields(self):
        self.create_user("alice")
        self.login()
        response = self.post_json("/api/cocktails/", {"name": "Mojito"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("required", response.json()["error"])

    def test_create_success(self):
        self.create_user("alice")
        self.login()
        response = self.post_json(
            "/api/cocktails/",
            {
                "name": "Mojito",
                "category": "Classic",
                "instructions": "Shake.",
                "ingredients": [{"id": self.ingredient.id, "quantity": "10 g"}],
            },
        )
        self.assertEqual(response.status_code, 201)

        cocktail = Cocktail.objects.get(name="Mojito")
        self.assertEqual(cocktail.author.username, "alice")
        ci = CocktailIngredient.objects.get(cocktail=cocktail)
        self.assertEqual(ci.ingredient, self.ingredient)
        self.assertEqual(ci.quantity, "10 g")

    def test_create_with_unknown_ingredient(self):
        self.create_user("alice")
        self.login()
        response = self.post_json(
            "/api/cocktails/",
            {
                "name": "Mojito",
                "category": "Classic",
                "instructions": "Shake.",
                "ingredients": [{"id": 9999, "quantity": "10 g"}],
            },
        )
        self.assertEqual(response.status_code, 404)


class CocktailListTests(BaseTestCase):
    def test_list_empty(self):
        response = self.client.get("/api/cocktails/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["items"], [])

    def test_list_includes_ingredients(self):
        ingredient = self.create_ingredient("Mint")
        self.create_cocktail("Mojito", ingredients=[(ingredient, "10 g")])

        response = self.client.get("/api/cocktails/")
        data = response.json()
        self.assertEqual(data["total"], 1)

        item = data["items"][0]
        self.assertEqual(item["name"], "Mojito")
        self.assertEqual(
            item["ingredients"],
            [{"ingredient_id": ingredient.id, "name": "Mint", "quantity": "10 g"}],
        )
        self.assertIsNone(item["author_id"])


class CocktailDetailTests(BaseTestCase):
    def setUp(self):
        self.ingredient = self.create_ingredient("Mint")
        self.author = self.create_user("alice")
        self.other = self.create_user("bob")
        self.cocktail = self.create_cocktail(
            "Mojito", author=self.author, ingredients=[(self.ingredient, "10 g")]
        )

    def test_retrieve(self):
        response = self.client.get(f"/api/cocktails/{self.cocktail.id}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Mojito")
        self.assertEqual(data["author_id"], self.author.id)
        self.assertEqual(data["ingredients"][0]["name"], "Mint")

    def test_retrieve_not_found(self):
        response = self.client.get("/api/cocktails/9999/")
        self.assertEqual(response.status_code, 404)

    def test_update_requires_auth(self):
        response = self.put_json(f"/api/cocktails/{self.cocktail.id}/", {"name": "X"})
        self.assertEqual(response.status_code, 401)

    def test_update_forbidden_for_non_author(self):
        self.login("bob")
        response = self.put_json(f"/api/cocktails/{self.cocktail.id}/", {"name": "X"})
        self.assertEqual(response.status_code, 403)

    def test_update_by_author(self):
        self.login("alice")
        response = self.put_json(
            f"/api/cocktails/{self.cocktail.id}/", {"name": "Classic Mojito"}
        )
        self.assertEqual(response.status_code, 200)
        self.cocktail.refresh_from_db()
        self.assertEqual(self.cocktail.name, "Classic Mojito")

    def test_update_by_admin(self):
        self.create_admin("admin")
        self.login("admin")
        response = self.put_json(
            f"/api/cocktails/{self.cocktail.id}/", {"name": "Admin Mojito"}
        )
        self.assertEqual(response.status_code, 200)

    def test_update_replaces_ingredients(self):
        new_ingredient = self.create_ingredient("Soda")
        self.login("alice")
        response = self.put_json(
            f"/api/cocktails/{self.cocktail.id}/",
            {"ingredients": [{"id": new_ingredient.id, "quantity": "100 ml"}]},
        )
        self.assertEqual(response.status_code, 200)

        cis = CocktailIngredient.objects.filter(cocktail=self.cocktail)
        self.assertEqual(cis.count(), 1)
        self.assertEqual(cis.first().ingredient, new_ingredient)

    def test_delete_requires_auth(self):
        response = self.client.delete(f"/api/cocktails/{self.cocktail.id}/")
        self.assertEqual(response.status_code, 401)

    def test_delete_forbidden_for_non_author(self):
        self.login("bob")
        response = self.client.delete(f"/api/cocktails/{self.cocktail.id}/")
        self.assertEqual(response.status_code, 403)

    def test_delete_by_author(self):
        self.login("alice")
        response = self.client.delete(f"/api/cocktails/{self.cocktail.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Cocktail.objects.filter(id=self.cocktail.id).exists())

    def test_delete_by_admin(self):
        self.create_admin("admin")
        self.login("admin")
        response = self.client.delete(f"/api/cocktails/{self.cocktail.id}/")
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Cocktail.objects.filter(id=self.cocktail.id).exists())
