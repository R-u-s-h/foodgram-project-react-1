from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag)
from foodgram.settings import EMPTY_VALUE
from users.models import User


@admin.register(User)
class UserClass(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
        'password',
    )
    list_editable = (
        'username',
        'first_name',
        'last_name',
        'email',
        'password',
    )
    search_fields = (
        'id',
        'username',
        'email',
    )
    empty_value_display = EMPTY_VALUE


@admin.register(Ingredient)
class IngredientClass(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',
    )
    list_filter = (
        'name',
        'measurement_unit',
    )
    list_editable = (
        'name',
        'measurement_unit',
    )
    search_fields = ('name',)
    ordering = ('id',)
    empty_value_display = EMPTY_VALUE


@admin.register(Tag)
class TagClass(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )
    list_filter = ('color',)
    list_editable = (
        'name',
        'color',
        'slug',
    )
    search_fields = ('name',)
    ordering = ('id',)
    empty_value_display = EMPTY_VALUE


@admin.register(Recipe)
class RecipeClass(admin.ModelAdmin):
    list_display = (
        'name',
        'text',
        'image',
        'cooking_time',
        'author'
    )
    list_filter = (
        'author',
        'name',
        'tags',
    )
    ordering = ('-id',)
    search_fields = ('name',)
    empty_value_display = EMPTY_VALUE


@admin.register(IngredientRecipe)
class IngredientRecipeClass(admin.ModelAdmin):
    list_display = (
        'id',
        'ingredient',
        'recipe',
        'amount',
    )
    list_filter = (
        'ingredient',
        'recipe',
        'amount',
    )
    ordering = ('-recipe',)
    empty_value_display = EMPTY_VALUE


@admin.register(Favorite)
class FavoriteClass(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
    )
    list_filter = (
        'user',
        'id',
    )
    ordering = ('-id',)
    empty_value_display = EMPTY_VALUE


@admin.register(ShoppingCart)
class ShoppingCartClass(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
    )
    list_filter = ('user', 'recipe')
    ordering = ('-id',)
    empty_value_display = EMPTY_VALUE
