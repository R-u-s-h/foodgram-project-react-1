from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from foodgram.settings import SLUG_ERROR
from users.models import User


class Tag(models.Model):
    name = models.TextField(
        'Название',
        max_length=200,
        blank=True,
        null=True
    )
    color = models.TextField(
        'Цвет в HEX',
        max_length=7,
        blank=True,
        null=True,
        default='#ffffff'
    )
    slug = models.TextField(
        'Уникальный идентификатор',
        max_length=200,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message=SLUG_ERROR,
            ),
        ],
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name[:15]


class Ingredient(models.Model):
    name = models.TextField(
        'Название',
        max_length=200,
        blank=True,
        null=True
    )
    measurement_unit = models.TextField(
        'Единица измерения',
        max_length=200,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name[:15]


class Recipe(models.Model):
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientRecipe',
        verbose_name='Ингредиенты',
        blank=True
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        blank=True
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='recipes/',
        editable=True,
        blank=True,
        null=True,
    )
    name = models.TextField(
        'Название',
        max_length=200
    )
    text = models.TextField(
        'Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления, мин.',
        validators=[MinValueValidator(1)],
        blank=True,
        null=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )

    class Meta:
        ordering = ('author',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name[:15]


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_recipe'
    )
    amount = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text='Количество',
    )

    class Meta:
        verbose_name = 'Ингредиенты рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe'
            )
        ]


class TagRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Recipe'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Tag'
    )

    class Meta:
        verbose_name = 'Тэг рецепта'
        verbose_name_plural = 'Тэг рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['tag', 'recipe'],
                name='unique_recipetag'
            )
        ]

    def __str__(self):
        return f'{self.tag} {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='cart'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='user_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user.username} {self.recipe.name}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites'
    )

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='user_favorite_recipe',
            )
        ]

    def __str__(self):
        return f'{self.recipe} {self.user}'
