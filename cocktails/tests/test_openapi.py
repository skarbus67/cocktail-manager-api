"""Tests for the OpenAPI schema and documentation endpoints."""

from django.test import TestCase


class OpenAPITests(TestCase):
    def test_schema_endpoint(self):
        response = self.client.get("/api/schema/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["openapi"], "3.0.3")
        self.assertEqual(data["info"]["title"], "Cocktail API")
        self.assertIn("/api/cocktails/", data["paths"])
        self.assertIn("/api/ingredients/", data["paths"])
        self.assertIn("/api/auth/register/", data["paths"])
        self.assertIn("/api/cocktails/{cocktail_id}/reviews/", data["paths"])

    def test_docs_endpoint(self):
        response = self.client.get("/api/docs/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response["Content-Type"])
        self.assertIn("SwaggerUIBundle", response.content.decode())
