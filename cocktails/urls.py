from django.urls import path
from .views import (
    IngredientListCreateView, IngredientDetailView,
        CocktailListCreateView, CocktailDetailView,
        RegisterView, LoginView, LogoutView, CocktailReviewView
)

urlpatterns = [
    # auth
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),

    # ingredients
    path('ingredients/', IngredientListCreateView.as_view(), name='ingredient-list-create'),
    path('ingredients/<int:ingredient_id>/', IngredientDetailView.as_view(), name='ingredient-detail'),
    
    # cocktails
    path('cocktails/', CocktailListCreateView.as_view(), name='cocktail-list-create'),
    path('cocktails/<int:cocktail_id>/', CocktailDetailView.as_view(), name='cocktail-detail'),
]



urlpatterns = [
    # auth
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),

    # ingredients
    path('ingredients/', IngredientListCreateView.as_view(), name='ingredient-list-create'),
    path('ingredients/<int:ingredient_id>/', IngredientDetailView.as_view(), name='ingredient-detail'),
    
    # cocktails
    path('cocktails/', CocktailListCreateView.as_view(), name='cocktail-list-create'),
    path('cocktails/<int:cocktail_id>/', CocktailDetailView.as_view(), name='cocktail-detail'),

    # reviews
    path('cocktails/<int:cocktail_id>/reviews/', CocktailReviewView.as_view(), name='cocktail-reviews'),
]