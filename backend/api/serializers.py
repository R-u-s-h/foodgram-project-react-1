from django.conf import settings
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.models import Follow, User
from recipes.models import (Ingredient, Tag, Recipe,
                            Favorite, ShoppingCart, IngredientRecipe)


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name',
                  'last_name', 'password')
        write_only_fields = ('password',)
        read_only_fields = ('id',)


class CustomUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user.id,
            author=obj.id
        ).exists()


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['recipe', 'user'],
                message=settings.WRONG_UNIQUE_RECEPIE
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=['recipe', 'user'],
                message=settings.WRONG_RECIPE_TO_SHOPPINGCART
            )
        ]


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name',
                  'image', 'cooking_time')


class FollowListSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'recipes',
                  'recipes_count')

    def get_recipes(self, obj):
        recipes = obj.author.recipes.all()
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        return RecipeShortSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()


class FollowSerializer(CustomUserSerializer):
    class Meta:
        model = Follow
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author'),
                message=settings.WRONG_FOLLOW
            )
        ]

    def to_representation(self, instance):
        return FollowListSerializer(instance).data


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name',
                  'measurement_unit')


class IngredientListSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name',
                  'measurement_unit',
                  'amount')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name',
                  'color', 'slug')


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'amount')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ("id", "amount")


class RecipeListSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer()
    ingredients = IngredientListSerializer(
        source='ingredient_recipe',
        many=True
    )
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name',
                  'image', 'text', 'ingredients',
                  'tags', 'cooking_time',
                  'is_in_shopping_cart',
                  'is_favorited')

    def _exist(self, model, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return model.objects.filter(
            user=request.user,
            recipe__id=obj.id
        ).exists()

    def get_is_favorited(self, obj):
        return self._exist(Favorite, obj)

    def get_is_in_shopping_cart(self, obj):
        return self._exist(ShoppingCart, obj)


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientRecipeSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients',
                  'tags', 'image', 'name',
                  'text', 'cooking_time')

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': settings.WRONG_INGREDIENT_CHOOSE
            })
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError({
                    'ingredients': settings.WRONG_UNIQUE_INGREDIENTS
                })
            ingredients_list.append(ingredient_id)
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError({
                    'amount': settings.WRONG_INGREDIENT_AMOUNT
                })
        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError({
                'tags': settings.WRONG_TAG_CHOOSE
            })
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError({
                    'tags': settings.WRONG_UNIQUE_TAGS
                })
            tags_list.append(tag)

        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) <= 0:
            raise serializers.ValidationError({
                'cooking_time': settings.WRONG_COOKING_TIME
            })
        return data

    def create_tags(self, recipe, tags):
        for tag in tags:
            recipe.tags.add(tag)

    def create_ingredients(self, recipe, ingredients):
        IngredientRecipe.objects.bulk_create(
            [IngredientRecipe(recipe=recipe,
             ingredient=get_object_or_404(
                Ingredient, pk=ingredient['id']),
             amount=ingredient['amount'])
             for ingredient in ingredients])

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **validated_data
        )
        recipe.tags.set(tags)
        self.create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        instance.tags.clear()
        IngredientRecipe.objects.filter(recipe=instance).delete()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.set(tags)
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeListSerializer(instance).data
