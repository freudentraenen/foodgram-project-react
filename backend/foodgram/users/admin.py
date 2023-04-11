from django.contrib import admin

from users.models import User, Follow


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'first_name',
        'last_name',
        'username',
        'email',
        'get_favorite_recipes',
        'get_shopping_cart'
    )
    search_fields = ('username',)
    empty_value_display = ''


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'following'
    )
    search_fields = ('user', 'following')
    empty_value_display = ''


admin.site.register(User, UserAdmin)
admin.site.register(Follow, FollowAdmin)
