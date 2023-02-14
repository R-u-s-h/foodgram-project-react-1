from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, DownloadShoppingCartViewSet,
                    FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                    ShoppingCartViewSet, TagViewSet)

app_name = 'api'
router_v1 = DefaultRouter()

router_v1.register(r'users', CustomUserViewSet, basename='users')
router_v1.register(r'tags', TagViewSet, basename='tags')
router_v1.register(r'recipes', RecipeViewSet, basename='recipes')
router_v1.register(r'ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path(
        'users/subscriptions/',
        CustomUserViewSet.as_view({'get': 'list'}),
        name='subscriptions'
    ),
    re_path(
        r'users/(?P<author_id>\d+)/subscribe/',
        CustomUserViewSet.as_view({'post': 'create', 'delete': 'delete'}),
        name='to_subscribe'
    ),
    re_path(
        r'recipes/(?P<recipe_id>\d+)/favorite/',
        FavoriteViewSet.as_view({'post': 'create', 'delete': 'delete'}),
        name='favorites'
    ),
    re_path(
        r'recipes/(?P<recipe_id>\d+)/shopping_cart/',
        ShoppingCartViewSet.as_view({'post': 'create', 'delete': 'delete'}),
        name='shopping_cart'
    ),
    path(
        'recipes/download_shopping_cart/',
        DownloadShoppingCartViewSet.as_view({'get': 'download'}),
        name='download'
    ),
    path('', include(router_v1.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
