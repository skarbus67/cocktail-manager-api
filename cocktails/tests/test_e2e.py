"""End-to-end tests that exercise the API over a real HTTP server.

These use Django's ``LiveServerTestCase`` to spin up an actual WSGI server and
drive it with plain ``urllib`` (no test-client shortcuts), including session
cookie handling, so the full request/response cycle is covered: URL routing,
middleware, views and the database.
"""

import http.cookiejar
import json
import urllib.error
import urllib.request

from django.test import LiveServerTestCase


class ApiClient:
    """Minimal HTTP client with cookie-based session support."""

    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")
        self.cookies = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookies)
        )

    def request(self, method, path, data=None):
        url = self.base_url + path
        body = None
        headers = {}
        if data is not None:
            body = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with self.opener.open(req, timeout=10) as resp:
                status = resp.status
                content = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            status = exc.code
            content = exc.read().decode("utf-8")

        payload = json.loads(content) if content else None
        return status, payload

    def get(self, path):
        return self.request("GET", path)

    def post(self, path, data=None):
        return self.request("POST", path, data)

    def put(self, path, data=None):
        return self.request("PUT", path, data)

    def delete(self, path):
        return self.request("DELETE", path)


class FullUserJourneyE2ETests(LiveServerTestCase):
    def setUp(self):
        self.api = ApiClient(self.live_server_url)

    def test_full_user_journey(self):
        api = self.api

        # Register a new user.
        status, payload = api.post(
            "/api/auth/register/",
            {"username": "e2euser", "password": "sup3r-secret", "email": "e2e@example.com"},
        )
        self.assertEqual(status, 201)

        # Log in (session cookie is stored automatically by the client).
        status, payload = api.post(
            "/api/auth/login/",
            {"username": "e2euser", "password": "sup3r-secret"},
        )
        self.assertEqual(status, 200)

        # Create an ingredient.
        status, payload = api.post(
            "/api/ingredients/", {"name": "Mint", "is_alcoholic": False}
        )
        self.assertEqual(status, 201)
        ingredient_id = payload["id"]

        # Create a cocktail while authenticated.
        status, payload = api.post(
            "/api/cocktails/",
            {
                "name": "Virgin Mojito",
                "category": "Mocktail",
                "instructions": "Muddle the mint.",
                "ingredients": [{"id": ingredient_id, "quantity": "10 g"}],
            },
        )
        self.assertEqual(status, 201)
        cocktail_id = payload["id"]

        # List cocktails.
        status, payload = api.get("/api/cocktails/")
        self.assertEqual(status, 200)
        self.assertIn("Virgin Mojito", [c["name"] for c in payload["items"]])

        # Retrieve cocktail detail.
        status, payload = api.get(f"/api/cocktails/{cocktail_id}/")
        self.assertEqual(status, 200)
        self.assertEqual(payload["ingredients"][0]["name"], "Mint")

        # Leave a review.
        status, payload = api.post(
            f"/api/cocktails/{cocktail_id}/reviews/",
            {"rating": 5, "content": "Refreshing!"},
        )
        self.assertEqual(status, 201)

        # List reviews.
        status, payload = api.get(f"/api/cocktails/{cocktail_id}/reviews/")
        self.assertEqual(status, 200)
        self.assertEqual(payload["items"][0]["rating"], 5)

        # Log out.
        status, payload = api.post("/api/auth/logout/")
        self.assertEqual(status, 200)

        # After logging out, creating a cocktail is forbidden.
        status, payload = api.post(
            "/api/cocktails/",
            {"name": "Forbidden", "category": "X", "instructions": "Y"},
        )
        self.assertEqual(status, 401)

    def test_authorization_between_users(self):
        api = self.api

        # Owner registers and creates a cocktail.
        api.post("/api/auth/register/", {"username": "owner", "password": "sup3r-secret"})
        api.post("/api/auth/login/", {"username": "owner", "password": "sup3r-secret"})

        status, payload = api.post("/api/ingredients/", {"name": "Rum", "is_alcoholic": True})
        self.assertEqual(status, 201)
        ingredient_id = payload["id"]

        status, payload = api.post(
            "/api/cocktails/",
            {
                "name": "Rum Cola",
                "category": "Classic",
                "instructions": "Mix.",
                "ingredients": [{"id": ingredient_id, "quantity": "50 ml"}],
            },
        )
        self.assertEqual(status, 201)
        cocktail_id = payload["id"]

        api.post("/api/auth/logout/")

        # A different user logs in.
        api.post("/api/auth/register/", {"username": "intruder", "password": "sup3r-secret"})
        api.post("/api/auth/login/", {"username": "intruder", "password": "sup3r-secret"})

        # They cannot edit or delete someone else's cocktail.
        status, _ = api.put(f"/api/cocktails/{cocktail_id}/", {"name": "Hacked"})
        self.assertEqual(status, 403)

        status, _ = api.delete(f"/api/cocktails/{cocktail_id}/")
        self.assertEqual(status, 403)
