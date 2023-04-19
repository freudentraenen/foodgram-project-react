import csv

from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.http import HttpResponse

from rest_framework import viewsets, status, permissions
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS

from django_filters.rest_framework import DjangoFilterBackend

from djoser.serializers import SetPasswordSerializer

from recipes.models import Recipe, Tag, Ingredient
from users.models import User, Follow
from .filters import RecipeFilter, IngredientSearchFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (RecipeReadSerializer, TagSerializer,
                          IngredientSerializer, UserSerializer,
                          RecipeFavoritesShoppingCartSerializer,
                          RecipeWriteSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeReadSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    http_method_names = (
        'get',
        'post',
        'patch',
        'delete'
    )
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    filterset_fields = ('author', 'tags')
    search_fields = (
        'author__username',
        'tags__slug',
        'is_favorited',
        'is_in_shopping_cart'
    )

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user
        )

    @action(methods=('get',), detail=False)
    def download_shopping_cart(self, request):
        recipes = Recipe.objects.filter(users_who_shopped=request.user)
        ingredients = recipes.values(
            'ingredients__ingredient__name',
            'ingredients__amount',
            'ingredients__ingredient__measurement_unit'
        )
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = ('attachment; '
                                           'filename="shopping_list.csv"')
        writer = csv.writer(response)
        writer.writerow(['Название', 'Количество'])
        for obj in ingredients:
            writer.writerow(
                obj['ingredients__ingredient__name'],
                obj['ingredients__amount'],
                obj['ingredients__ingredient__measurement_unit']
            )
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('name',)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = (
        'get',
        'post',
        'delete'
    )
    pagination_class = LimitOffsetPagination

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=('get',), detail=False,
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=('get',), detail=False,
            permission_classes=(permissions.IsAuthenticated,))
    def subscriptions(self, request):
        ids = request.user.follows.all().values_list(
            'following',
            flat=True
        )
        queryset = User.objects.filter(pk__in=ids)
        page = self.paginate_queryset(queryset)
        serializer = UserSerializer(
            page, context={'request': request}, many=True)
        return self.get_paginated_response(serializer.data)

    @action(methods=('post',), detail=False,
            permission_classes=(permissions.IsAuthenticated,),
            url_path=r'(?P<user_pk>\d+)/subscribe')
    def subscribe(self, request, user_pk):
        try:
            following = get_object_or_404(User, pk=user_pk)
            Follow.objects.create(
                user=request.user,
                following=following
            )
            serializer = UserSerializer(
                following, context={'request': request})
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        except ValidationError as err:
            return Response(
                {'errors': err.args[0]['__all__']},
                status=status.HTTP_400_BAD_REQUEST
            )

    @subscribe.mapping.delete
    def unsubscribe(self, request, user_pk):
        follow = Follow.objects.filter(
            user=request.user,
            following=get_object_or_404(User, pk=user_pk)
        )
        if follow.exists():
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Вы не подписаны на этого пользователя'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(methods=('post',), detail=False,
            permission_classes=(permissions.IsAuthenticated,))
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserList(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination


class UserDetail(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class APIFavoritesList(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, recipe_pk):

        if not request.user.favorite_recipes.filter(pk=recipe_pk).exists():
            recipe = get_object_or_404(Recipe, pk=recipe_pk)
            request.user.favorite_recipes.add(recipe)
            serializer = RecipeFavoritesShoppingCartSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {'detail': 'рецепт уже в избранном'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, recipe_pk):

        if request.user.favorite_recipes.filter(pk=recipe_pk).exists():
            request.user.favorite_recipes.remove(get_object_or_404(
                Recipe,
                pk=recipe_pk
            ))
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'рецепта нет в избранном'},
            status=status.HTTP_400_BAD_REQUEST
        )


class APIShoppingCart(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, recipe_pk):
        if not request.user.shopping_cart.filter(pk=recipe_pk).exists():
            recipe = get_object_or_404(Recipe, pk=recipe_pk)
            request.user.shopping_cart.add(recipe)
            serializer = RecipeFavoritesShoppingCartSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {'detail': 'рецепт уже в списке покупок'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, recipe_pk):
        if request.user.shopping_cart.filter(pk=recipe_pk).exists():
            request.user.shopping_cart.remove(get_object_or_404(
                Recipe,
                pk=recipe_pk
            ))
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'рецепта нет в списке покупок'},
            status=status.HTTP_400_BAD_REQUEST
        )
