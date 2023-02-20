from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import IngredientSearchFilter, RecipeFilter
from .serializers import (CustomUserSerializer, FavoriteSerializer,
                          FollowListSerializer, FollowSerializer,
                          IngredientSerializer, RecipeListSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          TagSerializer)
from .utils import download_cart
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Follow, User


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated, ),
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, pk=id)
        data = {
            'user': user.id,
            'author': author.id,
        }
        if request.method == 'POST':
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
        get_object_or_404(
            Follow,
            user=request.user,
            author=author
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated, )
    )
    def subscriptions(self, request):
        return self.get_paginated_response(
            FollowListSerializer(
                self.paginate_queryset(
                    Follow.objects.filter(user=request.user)
                ),
                many=True,
                context={'request': request}
            ).data
        )

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=(IsAuthenticated, )
    )
    def me(self, request):
        if request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        return Response(
            CustomUserSerializer(request.user).data,
            status=status.HTTP_200_OK
        )


@permission_classes([AllowAny, ])
class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


@permission_classes([AllowAny, ])
class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter, )
    search_fields = ('^name', )
    pagination_class = None


@permission_classes([IsAuthenticatedOrReadOnly, ])
class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    filterset_class = RecipeFilter
    filter_backends = (DjangoFilterBackend, )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeListSerializer
        return RecipeSerializer

    @staticmethod
    def create_object(serializers, user, recipe):
        data = {
            'user': user.id,
            'recipe': recipe.id,
        }
        serializer = serializers(
            data=data,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @staticmethod
    def delete_object(request, pk, model):
        get_object_or_404(
            model,
            user=request.user,
            recipe=get_object_or_404(Recipe, id=pk)
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('POST',),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return self.create_object(
            FavoriteSerializer,
            request.user,
            get_object_or_404(Recipe, id=pk)
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_object(
            request=request,
            pk=pk,
            model=Favorite
        )

    @action(
        detail=True,
        methods=('POST',),
        permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        return self.create_object(
            ShoppingCartSerializer,
            request.user,
            get_object_or_404(Recipe, id=pk)
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_object(
            request=request,
            pk=pk,
            model=ShoppingCart
        )

    @action(
        detail=False,
        methods=('GET',),
        permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        return download_cart(request)
