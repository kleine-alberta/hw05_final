from django.contrib import admin
from .models import Post, Group, Follow


class PostAdmin(admin.ModelAdmin):
    list_display = ("text", "pub_date", "author")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"


admin.site.register(Post, PostAdmin)


class GroupAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title",)
    empty_value_display = "-пусто-"


admin.site.register(Group, GroupAdmin)


class FollowAdmin(admin.ModelAdmin):
    list_display = ("author", "user")
    empty_value_display = "-пусто-"


admin.site.register(Follow, FollowAdmin)
