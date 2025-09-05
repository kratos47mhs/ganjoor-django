from rest_framework import serializers
from .models import (
    GanjoorPoet,
    GanjoorCat,
    GanjoorPoem,
    GanjoorVerse,
    GanjoorPoemAudio,
    GanjoorFavorite,
    UserSetting,
)


# -------------------
# Poet Serializer
# -------------------
class GanjoorPoetSerializer(serializers.ModelSerializer):
    poems_count = serializers.IntegerField(source="poems.count", read_only=True)

    class Meta:
        model = GanjoorPoet
        fields = ["id", "name", "bio", "birth_year", "death_year", "poems_count"]


class GanjoorCatSerializer(serializers.ModelSerializer):
    class Meta:
        model = GanjoorCat
        fields = ["id", "poet", "parent", "text", "slug"]


class GanjoorVerseSerializer(serializers.ModelSerializer):
    class Meta:
        model = GanjoorVerse
        fields = ["id", "poem", "text", "order", "position"]


# -------------------
# Poem Serializer
# -------------------
class GanjoorPoemSerializer(serializers.ModelSerializer):
    poet = GanjoorPoetSerializer(read_only=True)
    favorites_count = serializers.IntegerField(
        source="favorited_by.count", read_only=True
    )
    audio_files = serializers.SerializerMethodField()

    class Meta:
        model = GanjoorPoem
        fields = [
            "id",
            "title",
            "text",
            "poet",
            "has_comments",
            "favorites_count",
            "audio_files",
        ]

    def get_audio_files(self, obj):
        return GanjoorPoemAudioSerializer(obj.audio_files.all(), many=True).data


# -------------------
# Poem Audio Serializer
# -------------------
class GanjoorPoemAudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = GanjoorPoemAudio
        fields = ["id", "file", "narrator", "duration_seconds"]


# -------------------
# Favorite Serializer
# -------------------
class GanjoorFavoriteSerializer(serializers.ModelSerializer):
    poem = GanjoorPoemSerializer(read_only=True)
    poem_id = serializers.PrimaryKeyRelatedField(
        queryset=GanjoorPoem.objects.all(), write_only=True, source="poem"
    )

    class Meta:
        model = GanjoorFavorite
        fields = ["id", "poem", "poem_id", "created_at"]


# -------------------
# User Setting Serializer
# -------------------
class UserSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSetting
        fields = [
            "view_mode",
            "font_size",
            "show_line_numbers",
            "last_highlight",
            "browse_button_visible",
            "comments_button_visible",
            "copy_button_visible",
            "print_button_visible",
            "home_button_visible",
            "random_button_visible",
            "editor_button_visible",
            "download_button_visible",
        ]
