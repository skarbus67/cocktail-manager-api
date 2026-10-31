"""Shared helpers for the cocktail API tests."""

import json

from django.contrib.auth.models import User
from django.test import TestCase

from cocktails.models import Cocktail, CocktailIngredient, Ingredient


class BaseTestCase(TestCase):
    """Base test case providing JSON API helpers and fixtures."""

    # --- HTTP helpers -------------------------------------------------------

    def post_json(self, url, data):
        return self.client.post(url, data=json.dumps(data), content_type="application/json")

    def put_json(self, url, data):
        return self.client.put(url, data=json.dumps(data), content_type="application/json")

    # --- Auth helpers -------------------------------------------------------

    def register(self, username="alice", password="sup3r-secret", email="alice@example.com"):
        return self.post_json(
            "/api/auth/register/",
            {"username": username, "password": password, "email": email},
        )

    def login(self, username="alice", password="sup3r-secret"):
        return self.post_json(
            "/api/auth/login/",
            {"username": username, "password": password},
        )

    # --- Model fixtures -----------------------------------------------------

    def create_user(self, username, password="sup3r-secret", **kwargs):
        return User.objects.create_user(username=username, password=password, **kwargs)

    def create_admin(self, username="admin", password="sup3r-secret"):
        return User.objects.create_superuser(
            username=username, email="admin@example.com", password=password
        )

    def create_ingredient(self, name, description="", is_alcoholic=False):
        return Ingredient.objects.create(
            name=name, description=description, is_alcoholic=is_alcoholic
        )

    def create_cocktail(self, name, category="Classic", instructions="Mix well.",
                        author=None, ingredients=None):
        cocktail = Cocktail.objects.create(
            name=name, category=category, instructions=instructions, author=author
        )
        for ingredient, quantity in (ingredients or []):
            CocktailIngredient.objects.create(
                cocktail=cocktail, ingredient=ingredient, quantity=quantity
            )
        return cocktail
