from django.contrib import admin
from .models import GanjoorPoet, GanjoorCat, GanjoorPoem, GanjoorVerse, GanjoorFavorite


@admin.register(GanjoorPoet)
class GanjoorPoetAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(GanjoorCat)
class GanjoorCatAdmin(admin.ModelAdmin):
    list_display = ("id", "text", "poet", "parent")
    list_filter = ("poet",)
    search_fields = ("text",)


@admin.register(GanjoorPoem)
class GanjoorPoemAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category")
    list_filter = ("category",)
    search_fields = ("title",)


@admin.register(GanjoorVerse)
class GanjoorVerseAdmin(admin.ModelAdmin):
    list_display = ("id", "poem", "order", "position")
    list_filter = ("position",)
    search_fields = ("text",)


@admin.register(GanjoorFavorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "poem", "created_at")
    list_filter = ("created_at", "user")
    search_fields = ("poem__title", "user__username")
