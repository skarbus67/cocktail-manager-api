"""Unit tests for the cocktail models."""

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from cocktails.models import Cocktail, CocktailIngredient, Ingredient, Review


class IngredientModelTests(TestCase):
    def test_str_returns_name(self):
        ingredient = Ingredient.objects.create(name="Mint", description="Fresh mint")
        self.assertEqual(str(ingredient), "Mint")

    def test_defaults(self):
        ingredient = Ingredient.objects.create(name="Soda")
        self.assertFalse(ingredient.is_alcoholic)
        self.assertIsNone(ingredient.description)
        self.assertFalse(bool(ingredient.image))

    def test_alcoholic_flag_is_stored(self):
        ingredient = Ingredient.objects.create(name="Rum", is_alcoholic=True)
        self.assertTrue(ingredient.is_alcoholic)


class CocktailModelTests(TestCase):
    def test_str_returns_name(self):
        cocktail = Cocktail.objects.create(name="Mojito", category="Classic", instructions="Shake.")
        self.assertEqual(str(cocktail), "Mojito")

    def test_author_related_name(self):
        user = User.objects.create_user(username="alice", password="x")
        cocktail = Cocktail.objects.create(
            name="Mojito", category="Classic", instructions="Shake.", author=user
        )
        self.assertIn(cocktail, user.cocktails.all())

    def test_author_is_nullable(self):
        cocktail = Cocktail.objects.create(name="Mojito", category="Classic", instructions="Shake.")
        self.assertIsNone(cocktail.author)


class CocktailIngredientModelTests(TestCase):
    def setUp(self):
        self.ingredient = Ingredient.objects.create(name="Mint")
        self.cocktail = Cocktail.objects.create(
            name="Mojito", category="Classic", instructions="Shake."
        )

    def test_through_relationship_and_str(self):
        ci = CocktailIngredient.objects.create(
            cocktail=self.cocktail, ingredient=self.ingredient, quantity="10 g"
        )
        self.assertEqual(str(ci), "10 g Mint in Mojito")
        self.assertIn(self.ingredient, self.cocktail.ingredients.all())


class ReviewModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="x")
        self.cocktail = Cocktail.objects.create(
            name="Mojito", category="Classic", instructions="Shake."
        )

    def test_str(self):
        review = Review.objects.create(
            cocktail=self.cocktail, user=self.user, rating=4, content="Great!"
        )
        self.assertEqual(str(review), "4/5 for Mojito by alice")

    def test_rating_below_minimum_is_invalid(self):
        review = Review(cocktail=self.cocktail, user=self.user, rating=0, content="x")
        with self.assertRaises(ValidationError):
            review.full_clean()

    def test_rating_above_maximum_is_invalid(self):
        review = Review(cocktail=self.cocktail, user=self.user, rating=6, content="x")
        with self.assertRaises(ValidationError):
            review.full_clean()
