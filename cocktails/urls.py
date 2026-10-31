from django.urls import path
from .views import IngredientListCreateView, IngredientDetailView

urlpatterns = [
    path('ingredients/', IngredientListCreateView.as_view(), name='ingredient-list-create'),
    path('ingredients/<int:ingredient_id>/', IngredientDetailView.as_view(), name='ingredient-detail'),
]