from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views import View
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Ingredient, Cocktail, CocktailIngredient, Review
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


def _parse_pagination(request):
    """Validate and parse the ``page`` and ``per_page`` query parameters.

    Returns ``(page, per_page), None`` on success, or ``None, error_message``
    when the input is not a positive integer.
    """
    try:
        page = int(request.GET.get('page', '1'))
        per_page = int(request.GET.get('per_page', '10'))
    except (TypeError, ValueError):
        return None, "The 'page' and 'per_page' parameters must be integers."
    if page < 1 or per_page < 1:
        return None, "The 'page' and 'per_page' parameters must be positive integers."
    return (page, per_page), None


@method_decorator(csrf_exempt, name='dispatch')
class IngredientListCreateView(View):
    def get(self, request):
        pagination, error = _parse_pagination(request)
        if error:
            return JsonResponse({"error": error}, status=400)
        page_number, per_page = pagination
        
        ingredients = Ingredient.objects.all().order_by('id')
        paginator = Paginator(ingredients, per_page)
        page_obj = paginator.get_page(page_number)
        
        data = [
            {
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "is_alcoholic": item.is_alcoholic,
                "image": item.image # Usunięto .url
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
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You must be logged in to add an ingredient."}, status=401)

        try:
            data = json.loads(request.body)

            if not data.get('name'):
                return JsonResponse({"error": "The 'name' field is required."}, status=400)
                
            ingredient = Ingredient.objects.create(
                name=data['name'],
                description=data.get('description', ''),
                is_alcoholic=data.get('is_alcoholic', False),
                image=data.get('image', None) # Dodano odczyt pola image
            )
            
            return JsonResponse({
                "id": ingredient.id,
                "name": ingredient.name,
                "description": ingredient.description,
                "is_alcoholic": ingredient.is_alcoholic,
                "image": ingredient.image,
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class IngredientDetailView(View):
    def get(self, request, ingredient_id):
        ingredient = get_object_or_404(Ingredient, id=ingredient_id)
        return JsonResponse({
            "id": ingredient.id,
            "name": ingredient.name,
            "description": ingredient.description,
            "is_alcoholic": ingredient.is_alcoholic,
            "image": ingredient.image 
        })

    def put(self, request, ingredient_id):
        ingredient = get_object_or_404(Ingredient, id=ingredient_id)

        if not request.user.is_authenticated:
            return JsonResponse({"error": "You must be logged in to edit an ingredient."}, status=401)

        if not request.user.is_superuser:
            return JsonResponse({"error": "You do not have permission to edit this ingredient."}, status=403)

        try:
            data = json.loads(request.body)
            ingredient.name = data.get('name', ingredient.name)
            ingredient.description = data.get('description', ingredient.description)
            ingredient.is_alcoholic = data.get('is_alcoholic', ingredient.is_alcoholic)
            ingredient.image = data.get('image', ingredient.image) # Dodano przypisanie pola image
            ingredient.save()
            
            return JsonResponse({
                "id": ingredient.id,
                "name": ingredient.name,
                "description": ingredient.description,
                "is_alcoholic": ingredient.is_alcoholic,
                "image": ingredient.image,
            })
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)

    def delete(self, request, ingredient_id):
        ingredient = get_object_or_404(Ingredient, id=ingredient_id)

        if not request.user.is_authenticated:
            return JsonResponse({"error": "You must be logged in to delete an ingredient."}, status=401)

        if not request.user.is_superuser:
            return JsonResponse({"error": "You do not have permission to delete this ingredient."}, status=403)

        ingredient.delete()
        return JsonResponse({}, status=204)

@method_decorator(csrf_exempt, name='dispatch')
class CocktailListCreateView(View):
    def get(self, request):
        pagination, error = _parse_pagination(request)
        if error:
            return JsonResponse({"error": error}, status=400)
        page_number, per_page = pagination
        
        cocktails = Cocktail.objects.all()

        author_id = request.GET.get('author_id')
        if author_id:
            cocktails = cocktails.filter(author_id=author_id)

        ingredient_name = request.GET.get('ingredient')
        if ingredient_name:
            cocktails = cocktails.filter(ingredients__name__icontains=ingredient_name)

        is_alcoholic = request.GET.get('is_alcoholic')
        if is_alcoholic is not None:
            if is_alcoholic.lower() == 'false':
                cocktails = cocktails.exclude(ingredients__is_alcoholic=True)
            elif is_alcoholic.lower() == 'true':
                cocktails = cocktails.filter(ingredients__is_alcoholic=True)

        cocktails = cocktails.distinct()

        sort_by = request.GET.get('sort', 'id')
        allowed_sort_fields = ['id', '-id', 'name', '-name', 'category', '-category']
        if sort_by in allowed_sort_fields:
            cocktails = cocktails.order_by(sort_by)
        else:
            cocktails = cocktails.order_by('id')

        # Paginacja
        paginator = Paginator(cocktails, per_page)
        page_obj = paginator.get_page(page_number)
        
        data = []
        for item in page_obj:
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
                "author_id": item.author.id if item.author else None,
                "ingredients": ingredients_data
            })
            
        return JsonResponse({
            "items": data,
            "total": paginator.count,
            "page": page_obj.number,
            "pages": paginator.num_pages
        })

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You must be logged in to add a recipe."}, status=401)

        try:
            data = json.loads(request.body)
            
            if not all(k in data for k in ("name", "category", "instructions")):
                return JsonResponse({"error": "The 'name', 'category', and 'instructions' fields are required."}, status=400)
                
            cocktail = Cocktail.objects.create(
                name=data['name'],
                category=data['category'],
                instructions=data['instructions'],
                author=request.user
            )
            
            ingredients_data = data.get('ingredients', [])
            for ing in ingredients_data:
                ingredient = get_object_or_404(Ingredient, id=ing['id'])
                CocktailIngredient.objects.create(
                    cocktail=cocktail,
                    ingredient=ingredient,
                    quantity=ing.get('quantity', '')
                )
            
            return JsonResponse({"id": cocktail.id, "message": "Cocktail created successfully."}, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You must be logged in to add a recipe."}, status=401)

        try:
            data = json.loads(request.body)
            
            if not all(k in data for k in ("name", "category", "instructions")):
                return JsonResponse({"error": "The 'name', 'category', and 'instructions' fields are required."}, status=400)
                
            cocktail = Cocktail.objects.create(
                name=data['name'],
                category=data['category'],
                instructions=data['instructions'],
                author=request.user
            )
            
            ingredients_data = data.get('ingredients', [])
            for ing in ingredients_data:
                ingredient = get_object_or_404(Ingredient, id=ing['id'])
                CocktailIngredient.objects.create(
                    cocktail=cocktail,
                    ingredient=ingredient,
                    quantity=ing.get('quantity', '')
                )
            
            return JsonResponse({"id": cocktail.id, "message": "Cocktail created successfully."}, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)


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
            "author_id": cocktail.author.id if cocktail.author else None,
            "ingredients": ingredients_data
        })
        
    def put(self, request, cocktail_id):
        cocktail = get_object_or_404(Cocktail, id=cocktail_id)
        
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You must be logged in to edit a recipe."}, status=401)
            
        if cocktail.author != request.user and not request.user.is_superuser:
            return JsonResponse({"error": "You do not have permission to edit this cocktail."}, status=403)

        try:
            data = json.loads(request.body)
            cocktail.name = data.get('name', cocktail.name)
            cocktail.category = data.get('category', cocktail.category)
            cocktail.instructions = data.get('instructions', cocktail.instructions)
            cocktail.save()
            
            if 'ingredients' in data:
                CocktailIngredient.objects.filter(cocktail=cocktail).delete()
                for ing in data['ingredients']:
                    ingredient = get_object_or_404(Ingredient, id=ing['id'])
                    CocktailIngredient.objects.create(
                        cocktail=cocktail,
                        ingredient=ingredient,
                        quantity=ing.get('quantity', '')
                    )
            
            return JsonResponse({"id": cocktail.id, "message": "Updated successfully."})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)

    def delete(self, request, cocktail_id):
        cocktail = get_object_or_404(Cocktail, id=cocktail_id)
        
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You must be logged in to delete a recipe."}, status=401)
            
        if cocktail.author != request.user and not request.user.is_superuser:
            return JsonResponse({"error": "You do not have permission to delete this cocktail."}, status=403)
            
        cocktail.delete()
        return JsonResponse({}, status=204)



@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            email = data.get('email', '')

            if not username or not password:
                return JsonResponse({"error": "Username and password are required."}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({"error": "A user with that username already exists."}, status=400)

            user = User.objects.create_user(username=username, email=email, password=password)
            return JsonResponse({"message": "Registered successfully.", "user_id": user.id}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return JsonResponse({"message": "Logged in successfully.", "user_id": user.id})
            else:
                return JsonResponse({"error": "Invalid credentials."}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(View):
    def post(self, request):
        logout(request)
        return JsonResponse({"message": "Logged out successfully."})

@method_decorator(csrf_exempt, name='dispatch')
class CocktailReviewView(View):
    def get(self, request, cocktail_id):
        cocktail = get_object_or_404(Cocktail, id=cocktail_id)
        
        pagination, error = _parse_pagination(request)
        if error:
            return JsonResponse({"error": error}, status=400)
        page_number, per_page = pagination
        
        reviews = Review.objects.filter(cocktail=cocktail).order_by('-id')
        paginator = Paginator(reviews, per_page)
        page_obj = paginator.get_page(page_number)
        
        data = [
            {
                "id": r.id,
                "user": r.user.username,
                "rating": r.rating,
                "content": r.content
            } for r in page_obj
        ]
        
        return JsonResponse({
            "items": data,
            "total": paginator.count,
            "page": page_obj.number,
            "pages": paginator.num_pages
        })

    def post(self, request, cocktail_id):
        cocktail = get_object_or_404(Cocktail, id=cocktail_id)
        
        if not request.user.is_authenticated:
            return JsonResponse({"error": "You must be logged in to add a review."}, status=401)
            
        try:
            data = json.loads(request.body)
            rating = data.get('rating')
            content = data.get('content')
            
            if rating is None or not content:
                return JsonResponse({"error": "The 'rating' and 'content' fields are required."}, status=400)
                
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    return JsonResponse({"error": "Rating must be between 1 and 5."}, status=400)
            except ValueError:
                return JsonResponse({"error": "Rating must be an integer."}, status=400)
                
            review = Review.objects.create(
                cocktail=cocktail,
                user=request.user,
                rating=rating,
                content=content
            )
            
            return JsonResponse({
                "id": review.id,
                "message": "Review added successfully."
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)