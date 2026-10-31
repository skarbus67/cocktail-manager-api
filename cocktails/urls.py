from django.urls import path
from .views import (
    IngredientListCreateView, IngredientDetailView,
    CocktailListCreateView, CocktailDetailView
)

urlpatterns = [
    # ingredients
    path('ingredients/', IngredientListCreateView.as_view(), name='ingredient-list-create'),
    path('ingredients/<int:ingredient_id>/', IngredientDetailView.as_view(), name='ingredient-detail'),
    
    # cocktails
    path('cocktails/', CocktailListCreateView.as_view(), name='cocktail-list-create'),
    path('cocktails/<int:cocktail_id>/', CocktailDetailView.as_view(), name='cocktail-detail'),
]