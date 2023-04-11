from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (RecipeViewSet, TagViewSet,
                    IngredientViewSet, UserViewSet,
                    APIFavoritesList, APIShoppingCart)

app_name = 'api'

router_v1 = DefaultRouter()
router_v1.register(
    'recipes',
    RecipeViewSet,
    basename='recipes'
)
router_v1.register(
    'tags',
    TagViewSet,
    basename='tags'
)
router_v1.register(
    'ingredients',
    IngredientViewSet,
    basename='ingredients'
)
router_v1.register(
    'users',
    UserViewSet,
    basename='users'
)


users_patterns = [
    # path('subscriptions/', SubscriptionsList.as_view()),
    # path('<int:user_pk>/subscribe/', APISubscribe.as_view()),
]

recipes_patterns = [
    path('<int:recipe_pk>/favorite/', APIFavoritesList.as_view()),
    path('<int:recipe_pk>/shopping_cart/', APIShoppingCart.as_view()),
]

auth_patterns = [
    path('', include('djoser.urls.authtoken')),
]

urlpatterns = [
    path('auth/', include(auth_patterns)),
    path('users/', include(users_patterns)),
    path('recipes/', include(recipes_patterns)),
    path('', include(router_v1.urls)),
]
