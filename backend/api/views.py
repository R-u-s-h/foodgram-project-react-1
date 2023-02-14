from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from foodgram.settings import (DELETE_FOLLOWING, SUBSCRIBE_NOT_EXIST,
                               USER_NOT_EXIST)
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag)
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from users.models import Follow, User

from .filters import IngredientSearchFilter, RecipeFilter
from .serializers import (CustomUserSerializer, FavoriteSerializer,
                          FollowSerializer, FollowListSerializer,
                          IngredientSerializer, RecipeListSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          TagSerializer)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(methods=['POST', 'DELETE'], detail=True)
    def subscribe(self, request, id):

        if self.request.method == 'POST':
            try:
                author = User.objects.get(id=id)
            except User.DoesNotExist:
                return Response(
                    USER_NOT_EXIST,
                    status=status.HTTP_400_BAD_REQUEST,
                )
            data = {'user': request.user.id, 'author': author.id}
            serializer = FollowSerializer(
                data=data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        if self.request.method == 'DELETE':
            author = User.objects.get(id=id)
            try:
                following = Follow.objects.get(
                    user=request.user,
                    author=author
                )
            except Follow.DoesNotExist:
                return Response(
                    SUBSCRIBE_NOT_EXIST,
                    status=status.HTTP_400_BAD_REQUEST
                )
            following.delete()
            return Response(
                DELETE_FOLLOWING.format(author),
                status=status.HTTP_204_NO_CONTENT
            )

    @action(methods=['GET'], url_path='subscriptions', detail=False)
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowListSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


@permission_classes([AllowAny, ])
class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


@permission_classes([AllowAny, ])
class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny, )
    filter_backends = (IngredientSearchFilter, )
    search_fields = ('^name', )


@permission_classes([IsAuthenticatedOrReadOnly, ])
class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    filter_class = RecipeFilter
    filter_backends = (DjangoFilterBackend, )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeListSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


@permission_classes([IsAuthenticated, ])
class FavoriteCartViewSet(ModelViewSet):

    def create(self, request):
        recipe_id = self.kwargs.get('recipe_id')
        recipe = get_object_or_404(Recipe, id=recipe_id)
        self.model.objects.create(
            user=request.user,
            recipe=recipe
        )
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request):
        recipe_id = self.kwargs.get('recipe_id')
        user_id = request.user.id
        object = get_object_or_404(
            self.model, user__id=user_id, recipe__id=recipe_id
        )
        object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(FavoriteCartViewSet):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerializer


class FavoriteViewSet(FavoriteCartViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer


@permission_classes([IsAuthenticated, ])
class DownloadShoppingCartViewSet(ModelViewSet):

    @staticmethod
    def canvas_method(dictionary):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename = "cart.pdf"'
        begin_position_x, begin_position_y = 40, 650
        sheet = canvas.Canvas(response, pagesize=A4)
        pdfmetrics.registerFont(
            TTFont('FreeSans', 'data/FreeSans.ttf')
        )
        sheet.setFont('FreeSans', 36)
        sheet.setTitle('Список покупок')
        sheet.drawString(
            begin_position_x,
            begin_position_y + 40,
            'Список покупок: '
        )
        sheet.setFont('FreeSans', 20)
        for number, item in enumerate(dictionary, start=1):
            if begin_position_y < 100:
                begin_position_y = 700
                sheet.showPage()
                sheet.setFont('FreeSans', 24)
            sheet.drawString(
                begin_position_x,
                begin_position_y,
                f'{number}.  {item["ingredient__name"]} - '
                f'{item["ingredient_total"]}'
                f' {item["ingredient__measurement_unit"]}'
            )
            begin_position_y -= 30
        sheet.showPage()
        sheet.save()
        return response

    def download(self, request):
        result = IngredientRecipe.objects.filter(
            recipe__cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(
            ingredient_total=Sum('amount')
        )
        return self.canvas_method(result)
