"""Integration tests for the cocktail review endpoints."""

from cocktails.models import Review

from .base import BaseTestCase


class ReviewListTests(BaseTestCase):
    def setUp(self):
        self.cocktail = self.create_cocktail("Mojito")
        self.user = self.create_user("alice")
        Review.objects.create(
            cocktail=self.cocktail, user=self.user, rating=5, content="Perfect"
        )

    def test_list_reviews(self):
        response = self.client.get(f"/api/cocktails/{self.cocktail.id}/reviews/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 1)
        self.assertEqual(data["items"][0]["rating"], 5)
        self.assertEqual(data["items"][0]["user"], "alice")

    def test_list_reviews_empty(self):
        other = self.create_cocktail("Empty")
        response = self.client.get(f"/api/cocktails/{other.id}/reviews/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["items"], [])


class ReviewCreateTests(BaseTestCase):
    def setUp(self):
        self.cocktail = self.create_cocktail("Mojito")

    def test_create_requires_auth(self):
        response = self.post_json(
            f"/api/cocktails/{self.cocktail.id}/reviews/",
            {"rating": 5, "content": "Great!"},
        )
        self.assertEqual(response.status_code, 401)

    def test_create_requires_rating_and_content(self):
        self.create_user("alice")
        self.login()
        response = self.post_json(
            f"/api/cocktails/{self.cocktail.id}/reviews/", {"rating": 5}
        )
        self.assertEqual(response.status_code, 400)

    def test_create_rating_out_of_range(self):
        self.create_user("alice")
        self.login()
        response = self.post_json(
            f"/api/cocktails/{self.cocktail.id}/reviews/",
            {"rating": 6, "content": "Great!"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("between 1 and 5", response.json()["error"])

    def test_create_rating_not_integer(self):
        self.create_user("alice")
        self.login()
        response = self.post_json(
            f"/api/cocktails/{self.cocktail.id}/reviews/",
            {"rating": "five", "content": "Great!"},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "Rating must be an integer.")

    def test_create_success(self):
        self.create_user("alice")
        self.login()
        response = self.post_json(
            f"/api/cocktails/{self.cocktail.id}/reviews/",
            {"rating": 5, "content": "Great!"},
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Review.objects.filter(cocktail=self.cocktail, rating=5).exists()
        )
