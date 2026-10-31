"""OpenAPI 3.0 schema and documentation views for the Cocktail API."""

from django.http import HttpResponse, JsonResponse


SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Cocktail API",
        "version": "1.0.0",
        "description": "REST API for managing cocktails and their ingredients.",
    },
    "servers": [{"url": "/"}],
    "paths": {
        "/api/auth/register/": {
            "post": {
                "summary": "Register a new user",
                "operationId": "register",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["username", "password"],
                                "properties": {
                                    "username": {"type": "string"},
                                    "password": {"type": "string"},
                                    "email": {"type": "string"},
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "201": {"description": "Registered successfully."},
                    "400": {
                        "description": "Missing username/password or username already exists.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                },
            }
        },
        "/api/auth/login/": {
            "post": {
                "summary": "Log in (establishes a session cookie)",
                "operationId": "login",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["username", "password"],
                                "properties": {
                                    "username": {"type": "string"},
                                    "password": {"type": "string"},
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Logged in successfully."},
                    "401": {
                        "description": "Invalid credentials.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                },
            }
        },
        "/api/auth/logout/": {
            "post": {
                "summary": "Log out (destroys the session)",
                "operationId": "logout",
                "security": [{"cookieAuth": []}],
                "responses": {"200": {"description": "Logged out successfully."}},
            }
        },
        "/api/ingredients/": {
            "get": {
                "summary": "List ingredients (paginated, filterable, sortable)",
                "operationId": "listIngredients",
                "parameters": [
                    {"name": "page", "in": "query", "schema": {"type": "integer", "minimum": 1}},
                    {"name": "per_page", "in": "query", "schema": {"type": "integer", "minimum": 1}},
                    {"name": "name", "in": "query", "schema": {"type": "string"}, "description": "Case-insensitive substring match on name."},
                    {"name": "is_alcoholic", "in": "query", "schema": {"type": "string", "enum": ["true", "false"]}},
                    {"name": "sort", "in": "query", "schema": {"type": "string", "enum": ["id", "-id", "name", "-name", "is_alcoholic", "-is_alcoholic"]}},
                ],
                "responses": {
                    "200": {
                        "description": "Paginated list of ingredients.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/PaginatedIngredients"}
                            }
                        },
                    },
                    "400": {
                        "description": "Invalid pagination or filter value.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                },
            },
            "post": {
                "summary": "Create an ingredient (auth required)",
                "operationId": "createIngredient",
                "security": [{"cookieAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["name"],
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "is_alcoholic": {"type": "boolean"},
                                    "image": {"type": "string", "format": "uri"},
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "201": {
                        "description": "Created ingredient.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Ingredient"}
                            }
                        },
                    },
                    "400": {
                        "description": "Missing name or invalid JSON.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                    "401": {
                        "description": "Not authenticated.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                },
            },
        },
        "/api/ingredients/{ingredient_id}/": {
            "parameters": [
                {"name": "ingredient_id", "in": "path", "required": True, "schema": {"type": "integer"}}
            ],
            "get": {
                "summary": "Retrieve an ingredient",
                "operationId": "retrieveIngredient",
                "responses": {
                    "200": {
                        "description": "Ingredient.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Ingredient"}
                            }
                        },
                    },
                    "404": {"description": "Not found."},
                },
            },
            "put": {
                "summary": "Update an ingredient (admin only)",
                "operationId": "updateIngredient",
                "security": [{"cookieAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "description": {"type": "string"},
                                    "is_alcoholic": {"type": "boolean"},
                                    "image": {"type": "string", "format": "uri"},
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Updated ingredient.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Ingredient"}
                            }
                        },
                    },
                    "401": {
                        "description": "Not authenticated.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                    "403": {
                        "description": "Not an admin.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                    "404": {"description": "Not found."},
                },
            },
            "delete": {
                "summary": "Delete an ingredient (admin only)",
                "operationId": "deleteIngredient",
                "security": [{"cookieAuth": []}],
                "responses": {
                    "204": {"description": "Deleted."},
                    "401": {
                        "description": "Not authenticated.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                    "403": {
                        "description": "Not an admin.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                    "404": {"description": "Not found."},
                },
            },
        },
        "/api/cocktails/": {
            "get": {
                "summary": "List cocktails (paginated, filterable, sortable)",
                "operationId": "listCocktails",
                "parameters": [
                    {"name": "page", "in": "query", "schema": {"type": "integer", "minimum": 1}},
                    {"name": "per_page", "in": "query", "schema": {"type": "integer", "minimum": 1}},
                    {"name": "author_id", "in": "query", "schema": {"type": "integer"}, "description": "Filter by author."},
                    {"name": "ingredient", "in": "query", "schema": {"type": "string"}, "description": "Filter by ingredient name."},
                    {"name": "is_alcoholic", "in": "query", "schema": {"type": "string", "enum": ["true", "false"]}},
                    {"name": "sort", "in": "query", "schema": {"type": "string", "enum": ["id", "-id", "name", "-name", "category", "-category"]}},
                ],
                "responses": {
                    "200": {
                        "description": "Paginated list of cocktails.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/PaginatedCocktails"}
                            }
                        },
                    },
                    "400": {
                        "description": "Invalid pagination value.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                },
            },
            "post": {
                "summary": "Create a cocktail (auth required)",
                "operationId": "createCocktail",
                "security": [{"cookieAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["name", "category", "instructions"],
                                "properties": {
                                    "name": {"type": "string"},
                                    "category": {"type": "string"},
                                    "instructions": {"type": "string"},
                                    "ingredients": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "required": ["id"],
                                            "properties": {
                                                "id": {"type": "integer"},
                                                "quantity": {"type": "string"},
                                            },
                                        },
                                    },
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "201": {"description": "Cocktail created."},
                    "400": {
                        "description": "Missing required fields or invalid JSON.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                    "401": {
                        "description": "Not authenticated.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                    "404": {"description": "Referenced ingredient not found."},
                },
            },
        },
        "/api/cocktails/{cocktail_id}/": {
            "parameters": [
                {"name": "cocktail_id", "in": "path", "required": True, "schema": {"type": "integer"}}
            ],
            "get": {
                "summary": "Retrieve a cocktail",
                "operationId": "retrieveCocktail",
                "responses": {
                    "200": {
                        "description": "Cocktail.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Cocktail"}
                            }
                        },
                    },
                    "404": {"description": "Not found."},
                },
            },
            "put": {
                "summary": "Update a cocktail (author or admin)",
                "operationId": "updateCocktail",
                "security": [{"cookieAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "category": {"type": "string"},
                                    "instructions": {"type": "string"},
                                    "ingredients": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "required": ["id"],
                                            "properties": {
                                                "id": {"type": "integer"},
                                                "quantity": {"type": "string"},
                                            },
                                        },
                                    },
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Updated cocktail."},
                    "401": {
                        "description": "Not authenticated.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                    "403": {
                        "description": "Not the author and not an admin.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                    "404": {"description": "Not found."},
                },
            },
            "delete": {
                "summary": "Delete a cocktail (author or admin)",
                "operationId": "deleteCocktail",
                "security": [{"cookieAuth": []}],
                "responses": {
                    "204": {"description": "Deleted."},
                    "401": {
                        "description": "Not authenticated.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                    "403": {
                        "description": "Not the author and not an admin.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                    "404": {"description": "Not found."},
                },
            },
        },
        "/api/cocktails/{cocktail_id}/reviews/": {
            "parameters": [
                {"name": "cocktail_id", "in": "path", "required": True, "schema": {"type": "integer"}}
            ],
            "get": {
                "summary": "List reviews for a cocktail (paginated)",
                "operationId": "listReviews",
                "parameters": [
                    {"name": "page", "in": "query", "schema": {"type": "integer", "minimum": 1}},
                    {"name": "per_page", "in": "query", "schema": {"type": "integer", "minimum": 1}},
                ],
                "responses": {
                    "200": {
                        "description": "Paginated list of reviews.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/PaginatedReviews"}
                            }
                        },
                    },
                    "400": {
                        "description": "Invalid pagination value.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                    "404": {"description": "Cocktail not found."},
                },
            },
            "post": {
                "summary": "Add a review (auth required)",
                "operationId": "createReview",
                "security": [{"cookieAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["rating", "content"],
                                "properties": {
                                    "rating": {"type": "integer", "minimum": 1, "maximum": 5},
                                    "content": {"type": "string"},
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "201": {"description": "Review added."},
                    "400": {
                        "description": "Missing fields or rating out of range.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                    "401": {
                        "description": "Not authenticated.",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/Error"}
                            }
                        },
                    },
                    "404": {"description": "Cocktail not found."},
                },
            },
        },
    },
    "components": {
        "securitySchemes": {
            "cookieAuth": {
                "type": "apiKey",
                "in": "cookie",
                "name": "sessionid",
            }
        },
        "schemas": {
            "Ingredient": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "description": {"type": "string", "nullable": True},
                    "is_alcoholic": {"type": "boolean"},
                    "image": {"type": "string", "nullable": True},
                },
            },
            "PaginatedIngredients": {
                "type": "object",
                "properties": {
                    "items": {"type": "array", "items": {"$ref": "#/components/schemas/Ingredient"}},
                    "total": {"type": "integer"},
                    "page": {"type": "integer"},
                    "pages": {"type": "integer"},
                },
            },
            "CocktailIngredient": {
                "type": "object",
                "properties": {
                    "ingredient_id": {"type": "integer"},
                    "name": {"type": "string"},
                    "quantity": {"type": "string"},
                },
            },
            "Cocktail": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                    "category": {"type": "string"},
                    "instructions": {"type": "string"},
                    "author_id": {"type": "integer", "nullable": True},
                    "ingredients": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/CocktailIngredient"},
                    },
                },
            },
            "PaginatedCocktails": {
                "type": "object",
                "properties": {
                    "items": {"type": "array", "items": {"$ref": "#/components/schemas/Cocktail"}},
                    "total": {"type": "integer"},
                    "page": {"type": "integer"},
                    "pages": {"type": "integer"},
                },
            },
            "Review": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "user": {"type": "string"},
                    "rating": {"type": "integer"},
                    "content": {"type": "string"},
                },
            },
            "PaginatedReviews": {
                "type": "object",
                "properties": {
                    "items": {"type": "array", "items": {"$ref": "#/components/schemas/Review"}},
                    "total": {"type": "integer"},
                    "page": {"type": "integer"},
                    "pages": {"type": "integer"},
                },
            },
            "Error": {
                "type": "object",
                "properties": {"error": {"type": "string"}},
            },
        },
    },
}


def openapi_schema(request):
    """Return the OpenAPI document as JSON."""
    return JsonResponse(SPEC)


_SWAGGER_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Cocktail API — Documentation</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css"/>
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    window.onload = () => {
      SwaggerUIBundle({
        url: "/api/schema/",
        dom_id: "#swagger-ui",
        deepLinking: true,
      });
    };
  </script>
</body>
</html>
"""


def swagger_ui(request):
    """Serve the Swagger UI page."""
    return HttpResponse(_SWAGGER_HTML, content_type="text/html")
