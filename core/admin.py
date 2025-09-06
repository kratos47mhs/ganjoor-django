from django.contrib import admin
from .models import (
    GanjoorPoet,
    GanjoorCategory,
    GanjoorPoem,
    GanjoorVerse,
    GanjoorFavorite,
    GanjoorPoemAudio,
    GanjoorAudioSync,
    UserSetting,
    Gil,
    Gver,
)

@admin.register(GanjoorPoet)
class GanjoorPoetAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    search_fields = ('name',)
    list_filter = ('category',)

@admin.register(GanjoorCategory)
class GanjoorCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'poet', 'parent', 'url')
    search_fields = ('title', 'url')
    list_filter = ('poet', 'parent')

@admin.register(GanjoorPoem)
class GanjoorPoemAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')
    search_fields = ('title',)
    list_filter = ('category',)

@admin.register(GanjoorVerse)
class GanjoorVerseAdmin(admin.ModelAdmin):
    list_display = ('poem', 'order', 'position')
    search_fields = ('poem__title', 'text')
    list_filter = ('poem',)

@admin.register(GanjoorFavorite)
class GanjoorFavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'poem', 'verse', 'verse_position', 'created_at')
    search_fields = ('user__username', 'poem__title')
    list_filter = ('user', 'poem')

@admin.register(GanjoorPoemAudio)
class GanjoorPoemAudioAdmin(admin.ModelAdmin):
    list_display = ('poem', 'file', 'is_uploaded')
    search_fields = ('poem__title', 'description')
    list_filter = ('is_uploaded',)

@admin.register(GanjoorAudioSync)
class GanjoorAudioSyncAdmin(admin.ModelAdmin):
    list_display = ('poem', 'audio', 'verse_order', 'millisec')
    list_filter = ('poem', 'audio')

@admin.register(UserSetting)
class UserSettingAdmin(admin.ModelAdmin):
    list_display = ('user', 'view_mode', 'font_size', 'show_line_numbers')
    search_fields = ('user__username',)

@admin.register(Gil)
class GilAdmin(admin.ModelAdmin):
    list_display = ('id', 'category')

@admin.register(Gver)
class GverAdmin(admin.ModelAdmin):
    list_display = ('id', 'current_version')