from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Group

from recipes.models import (
    Favorite, Ingredient, IngredientRecipe, Recipe, ShoppingCart, Tag
)
from users.models import Follow, User


class RecipeIngredientsInline(admin.TabularInline):
    model = Recipe.ingredients.through
    extra = 1
    min_num = 1


@admin.register(User)
class UserClass(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
        'password',
        'get_recipes',
        'get_followers'
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
    empty_value_display = settings.EMPTY_VALUE

    def get_recipes(self, obj):
        return obj.recipes.count()

    def get_followers(self, obj):
        return obj.following.count()

    get_recipes.short_description = 'Рецепты'
    get_followers.short_description = 'Подписчики'


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
    empty_value_display = settings.EMPTY_VALUE


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
    empty_value_display = settings.EMPTY_VALUE


@admin.register(Recipe)
class RecipeClass(admin.ModelAdmin):
    inlines = (RecipeIngredientsInline, )
    list_display = (
        'name',
        'text',
        'get_ingredients',
        'cooking_time',
        'author',
        'get_favorite',
    )
    list_filter = (
        'author',
        'name',
        'tags',
    )
    ordering = ('-id',)
    search_fields = ('name',)
    empty_value_display = settings.EMPTY_VALUE

    @admin.display(description='Избранное')
    def get_favorite(self, obj):
        return obj.favorite.count()

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        return ', '.join(obj.ingredients.all().values_list('name', flat=True))


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
    empty_value_display = settings.EMPTY_VALUE


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
    empty_value_display = settings.EMPTY_VALUE


@admin.register(ShoppingCart)
class ShoppingCartClass(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'recipe',
    )
    list_filter = ('user', 'recipe')
    ordering = ('-id',)
    empty_value_display = settings.EMPTY_VALUE


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'author_id')


admin.site.unregister(Group)
