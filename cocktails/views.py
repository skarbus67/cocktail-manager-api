from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views import View
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Ingredient
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