from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views import View
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Ingredient, Cocktail, CocktailIngredient
from django.shortcuts import get_object_or_404

@method_decorator(csrf_exempt, name='dispatch')
class IngredientListCreateView(View):
    def get(self, request):
        page_number = request.GET.get('page', 1)
        per_page = request.GET.get('per_page', 10)
        
        ingredients = Ingredient.objects.all().order_by('id')
        paginator = Paginator(ingredients, per_page)
        page_obj = paginator.get_page(page_number)
        
        data = [
            {
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "is_alcoholic": item.is_alcoholic,
                "image": item.image.url if item.image else None
            }
            for item in page_obj
        ]
        
        return JsonResponse({
            "items": data,
            "total": paginator.count,
            "page": page_obj.number,
            "pages": paginator.num_pages
        })

    def post(self, request):
        try:
            data = json.loads(request.body)
            
            if not data.get('name'):
                return JsonResponse({"error": "Pole 'name' jest wymagane."}, status=400)
                
            ingredient = Ingredient.objects.create(
                name=data['name'],
                description=data.get('description', ''),
                is_alcoholic=data.get('is_alcoholic', False)
            )
            
            return JsonResponse({
                "id": ingredient.id,
                "name": ingredient.name,
                "description": ingredient.description,
                "is_alcoholic": ingredient.is_alcoholic,
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({"error": "Nieprawidłowy format JSON."}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class IngredientDetailView(View):
    def get(self, request, ingredient_id):
        ingredient = get_object_or_404(Ingredient, id=ingredient_id)
        return JsonResponse({
            "id": ingredient.id,
            "name": ingredient.name,
            "description": ingredient.description,
            "is_alcoholic": ingredient.is_alcoholic,
            "image": ingredient.image.url if ingredient.image else None
        })

    def put(self, request, ingredient_id):
        ingredient = get_object_or_404(Ingredient, id=ingredient_id)
        try:
            data = json.loads(request.body)
            ingredient.name = data.get('name', ingredient.name)
            ingredient.description = data.get('description', ingredient.description)
            ingredient.is_alcoholic = data.get('is_alcoholic', ingredient.is_alcoholic)
            ingredient.save()
            
            return JsonResponse({
                "id": ingredient.id,
                "name": ingredient.name,
                "description": ingredient.description,
                "is_alcoholic": ingredient.is_alcoholic,
            })
        except json.JSONDecodeError:
            return JsonResponse({"error": "Nieprawidłowy format JSON."}, status=400)

    def delete(self, request, ingredient_id):
        ingredient = get_object_or_404(Ingredient, id=ingredient_id)
        ingredient.delete()
        return JsonResponse({}, status=204)

@method_decorator(csrf_exempt, name='dispatch')
class CocktailListCreateView(View):
    def get(self, request):
        page_number = request.GET.get('page', 1)
        per_page = request.GET.get('per_page', 10)
        
        cocktails = Cocktail.objects.all().order_by('id')
        paginator = Paginator(cocktails, per_page)
        page_obj = paginator.get_page(page_number)
        
        data = []
        for item in page_obj:
            # Pobieranie powiązanych składników i ich ilości
            ingredients_data = [
                {
                    "ingredient_id": ci.ingredient.id, 
                    "name": ci.ingredient.name, 
                    "quantity": ci.quantity
                }
                for ci in CocktailIngredient.objects.filter(cocktail=item)
            ]
            data.append({
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "instructions": item.instructions,
                "ingredients": ingredients_data
            })
            
        return JsonResponse({
            "items": data,
            "total": paginator.count,
            "page": page_obj.number,
            "pages": paginator.num_pages
        })

    def post(self, request):
        try:
            data = json.loads(request.body)
            
            if not all(k in data for k in ("name", "category", "instructions")):
                return JsonResponse({"error": "Pola 'name', 'category' i 'instructions' są wymagane."}, status=400)
                
            cocktail = Cocktail.objects.create(
                name=data['name'],
                category=data['category'],
                instructions=data['instructions']
            )
            
            # Zapisywanie relacji ze składnikami (oczekujemy listy słowników: [{"id": 1, "quantity": "50ml"}])
            ingredients_data = data.get('ingredients', [])
            for ing in ingredients_data:
                ingredient = get_object_or_404(Ingredient, id=ing['id'])
                CocktailIngredient.objects.create(
                    cocktail=cocktail,
                    ingredient=ingredient,
                    quantity=ing.get('quantity', '')
                )
            
            return JsonResponse({"id": cocktail.id, "message": "Koktajl utworzony pomyślnie."}, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({"error": "Nieprawidłowy format JSON."}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class CocktailDetailView(View):
    def get(self, request, cocktail_id):
        cocktail = get_object_or_404(Cocktail, id=cocktail_id)
        ingredients_data = [
            {
                "ingredient_id": ci.ingredient.id, 
                "name": ci.ingredient.name, 
                "quantity": ci.quantity
            }
            for ci in CocktailIngredient.objects.filter(cocktail=cocktail)
        ]
        return JsonResponse({
            "id": cocktail.id,
            "name": cocktail.name,
            "category": cocktail.category,
            "instructions": cocktail.instructions,
            "ingredients": ingredients_data
        })
        
    def put(self, request, cocktail_id):
        cocktail = get_object_or_404(Cocktail, id=cocktail_id)
        try:
            data = json.loads(request.body)
            cocktail.name = data.get('name', cocktail.name)
            cocktail.category = data.get('category', cocktail.category)
            cocktail.instructions = data.get('instructions', cocktail.instructions)
            cocktail.save()
            
            if 'ingredients' in data:
                # Najprostszy sposób aktualizacji: usuwamy stare relacje i tworzymy nowe
                CocktailIngredient.objects.filter(cocktail=cocktail).delete()
                for ing in data['ingredients']:
                    ingredient = get_object_or_404(Ingredient, id=ing['id'])
                    CocktailIngredient.objects.create(
                        cocktail=cocktail,
                        ingredient=ingredient,
                        quantity=ing.get('quantity', '')
                    )
            
            return JsonResponse({"id": cocktail.id, "message": "Zaktualizowano pomyślnie."})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Nieprawidłowy format JSON."}, status=400)

    def delete(self, request, cocktail_id):
        cocktail = get_object_or_404(Cocktail, id=cocktail_id)
        cocktail.delete()
        return JsonResponse({}, status=204)