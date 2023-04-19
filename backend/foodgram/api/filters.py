from django_filters import rest_framework

from rest_framework.filters import SearchFilter

from recipes.models import Recipe


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(rest_framework.FilterSet):
    author = rest_framework.NumberFilter(field_name='author__pk')
    tags = rest_framework.CharFilter(method='filter_tags')
    is_favorited = rest_framework.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = rest_framework.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'tags'
        )

    def filter_tags(self, queryset, name, value):
        return queryset.filter(tags__slug__in=self.request.GET.getlist('tags'))

    def filter_is_favorited(self, queryset, name, value):
        if value == 1:
            queryset = queryset.filter(users_who_favorited=self.request.user)
            return queryset
        if value == 0:
            queryset = queryset.exclude(users_who_favorited=self.request.user)
            return queryset
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value == 1:
            queryset = queryset.filter(users_who_shopped=self.request.user)
            return queryset
        if value == 0:
            queryset = queryset.exclude(users_who_shopped=self.request.user)
            return queryset
        return queryset
