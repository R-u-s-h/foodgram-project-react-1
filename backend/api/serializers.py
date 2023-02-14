from djoser.serializers import UserCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.models import Follow, User
from recipes.models import (Ingredient, Tag, Recipe,
                            Favorite, ShoppingCart, IngredientRecipe)
from foodgram.settings import (WRONG_INGREDIENT_CHOOSE,
                               WRONG_TAG_CHOOSE,
                               WRONG_UNIQUE_INGREDIENTS,
                               WRONG_INGREDIENT_AMOUNT,
                               WRONG_UNIQUE_TAGS, WRONG_COOKING_TIME)


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
        return Follow.objects.filter(user=request.user, author=obj).exists()


class FavoriteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    cooking_time = serializers.IntegerField()
    image = Base64ImageField(
        max_length=None,
        use_url=False
    )


class ShoppingCartSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    cooking_time = serializers.IntegerField()
    image = Base64ImageField(
        max_length=None,
        use_url=False
    )


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('user', 'following')

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return FollowListSerializer(
            instance.following, context=context).data


class FollowListSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed', 'recipes',
                  'recipes_count')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user,
            following=obj
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        context = {'request': request}
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is not None:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        else:
            recipes = obj.recipes.all()
        return FollowSerializer(
            recipes, many=True, context=context).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class IngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    measurement_unit = serializers.CharField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name',
                  'measurement_unit')


class IngredientListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
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


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientListSerializer(many=True)
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
                'ingredients': WRONG_INGREDIENT_CHOOSE
            })
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError({
                    'ingredients': WRONG_UNIQUE_INGREDIENTS
                })
            ingredients_list.append(ingredient_id)
            if int(ingredient['amount']) <= 0:
                raise serializers.ValidationError({
                    'amount': WRONG_INGREDIENT_AMOUNT
                })

        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError({
                'tags': WRONG_TAG_CHOOSE
            })
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise serializers.ValidationError({
                    'tags': WRONG_UNIQUE_TAGS
                })
            tags_list.append(tag)

        cooking_time = self.initial_data.get('cooking_time')
        if int(cooking_time) <= 0:
            raise serializers.ValidationError({
                'cooking_time': WRONG_COOKING_TIME
            })

        return data

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            amount = ingredient['amount']
            IngredientRecipe.objects.create(
                recipe=recipe,
                ingredient=ingredient_id,
                amount=amount
            )

    def create_tags(self, tags, recipe):
        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **validated_data
        )
        self.create_tags(validated_data.pop('tags'), recipe)
        self.create_ingredients(
            validated_data.pop('ingredients'),
            recipe
        )
        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )

        instance.tags.clear()
        self.create_tags(validated_data.get('tags'), instance)

        IngredientRecipe.objects.filter(recipe=instance).all().delete()
        self.create_ingredients(
            validated_data.get('ingredients'),
            instance
        )

        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeListSerializer(
            instance,
            context=context
        ).data


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

    def get_is_favorited(self, obj):
        user = self.context.get('request').user.id
        return Favorite.objects.filter(user=user, recipe=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user.id
        return ShoppingCart.objects.filter(user=user, recipe=obj.id).exists()
