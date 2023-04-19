from django_filters import rest_framework

from rest_framework.filters import SearchFilter

from recipes.models import Recipe


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(rest_framework.FilterSet):
    author = rest_framework.NumberFilter(field_name='author__pk')
    tags = rest_framework.CharFilter(
        field_name='tags__slug', lookup_expr='in', distinct=True)
    is_favorited = rest_framework.NumberFilter(method='get_is_favorited')
    is_in_shopping_cart = rest_framework.NumberFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags'
        )

    def get_is_favorited(self, queryset, name, value):
        if value == 1:
            queryset = queryset.filter(users_who_favorited=self.request.user)
            return queryset
        if value == 0:
            queryset = queryset.exclude(users_who_favorited=self.request.user)
            return queryset
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value == 1:
            queryset = queryset.filter(users_who_shopped=self.request.user)
            return queryset
        if value == 0:
            queryset = queryset.exclude(users_who_shopped=self.request.user)
            return queryset
        return queryset
