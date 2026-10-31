from django.db import models
from django.contrib.auth.models import User

class Ingredient(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    is_alcoholic = models.BooleanField(default=False)
    image = models.ImageField(upload_to='ingredients/', blank=True, null=True) 

    def __str__(self):
        return self.name

class Cocktail(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    instructions = models.TextField()
    ingredients = models.ManyToManyField(Ingredient, through='CocktailIngredient')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cocktails', null=True, blank=True)

    def __str__(self):
        return self.name

class CocktailIngredient(models.Model):
    cocktail = models.ForeignKey(Cocktail, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.quantity} {self.ingredient.name} in {self.cocktail.name}"