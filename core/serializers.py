"""
Serializers for the Ganjoor API.

This module contains all DRF serializers for the core models,
with proper field definitions, validation, and nested representations.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import (
    GanjoorPoet,
    GanjoorCategory,
    GanjoorPoem,
    GanjoorVerse,
    GanjoorFavorite,
    GanjoorPoemAudio,
    GanjoorAudioSync,
    UserSetting,
    VersePosition,
)


# -------------------
# User Serializer
# -------------------
class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with limited fields for security."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "date_joined"]
        read_only_fields = ["id", "date_joined"]


# -------------------
# Poet Serializers
# -------------------
class GanjoorPoetListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for poet list views."""

    poems_count = serializers.SerializerMethodField()

    class Meta:
        model = GanjoorPoet
        fields = ["id", "name", "century", "image", "image_slug", "poems_count"]
        read_only_fields = ["id"]

    def get_poems_count(self, obj):
        """Get total number of poems for this poet."""
        return GanjoorPoem.objects.filter(category__poet=obj).count()


class GanjoorPoetSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual poet views."""

    categories_count = serializers.SerializerMethodField()
    poems_count = serializers.SerializerMethodField()
    century_display = serializers.CharField(
        source="get_century_display", read_only=True
    )

    class Meta:
        model = GanjoorPoet
        fields = [
            "id",
            "name",
            "description",
            "century",
            "century_display",
            "image",
            "image_slug",
            "categories_count",
            "poems_count",
        ]
        read_only_fields = ["id"]

    def get_categories_count(self, obj):
        """Get total number of categories for this poet."""
        return obj.categories.count()

    def get_poems_count(self, obj):
        """Get total number of poems for this poet."""
        return GanjoorPoem.objects.filter(category__poet=obj).count()

    def validate_name(self, value):
        """Validate poet name is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError(_("Poet name cannot be empty."))
        return value.strip()


# -------------------
# Category Serializers
# -------------------
class GanjoorCategoryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for category list views."""

    poet_name = serializers.CharField(source="poet.name", read_only=True)
    parent_title = serializers.CharField(
        source="parent.title", read_only=True, allow_null=True
    )

    class Meta:
        model = GanjoorCategory
        fields = ["id", "title", "url", "poet", "poet_name", "parent", "parent_title"]
        read_only_fields = ["id"]


class GanjoorCategorySerializer(serializers.ModelSerializer):
    """Detailed serializer for individual category views."""

    poet_name = serializers.CharField(source="poet.name", read_only=True)
    parent_title = serializers.CharField(
        source="parent.title", read_only=True, allow_null=True
    )
    children = serializers.SerializerMethodField()
    poems_count = serializers.SerializerMethodField()
    breadcrumbs = serializers.SerializerMethodField()

    class Meta:
        model = GanjoorCategory
        fields = [
            "id",
            "title",
            "url",
            "poet",
            "poet_name",
            "parent",
            "parent_title",
            "children",
            "poems_count",
            "breadcrumbs",
        ]
        read_only_fields = ["id"]

    def get_children(self, obj):
        """Get child categories."""
        children = obj.children.all()
        return GanjoorCategoryListSerializer(children, many=True).data

    def get_poems_count(self, obj):
        """Get number of poems directly in this category."""
        return obj.poems.count()

    def get_breadcrumbs(self, obj):
        """Get breadcrumb trail for this category."""
        breadcrumbs = []
        current = obj
        while current:
            breadcrumbs.insert(0, {"id": current.id, "title": current.title})
            current = current.parent
        return breadcrumbs

    def validate_title(self, value):
        """Validate category title is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError(_("Category title cannot be empty."))
        return value.strip()


# -------------------
# Verse Serializers
# -------------------
class GanjoorVerseSerializer(serializers.ModelSerializer):
    """Serializer for verses with position information."""

    position_display = serializers.CharField(
        source="get_position_display", read_only=True
    )

    class Meta:
        model = GanjoorVerse
        fields = ["id", "poem", "order", "position", "position_display", "text"]
        read_only_fields = ["id"]

    def validate_text(self, value):
        """Validate verse text is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError(_("Verse text cannot be empty."))
        return value.strip()

    def validate_order(self, value):
        """Validate verse order is positive."""
        if value < 0:
            raise serializers.ValidationError(
                _("Verse order must be a positive number.")
            )
        return value

    def validate(self, data):
        """Validate verse doesn't duplicate order in same poem."""
        if self.instance is None:  # Creating new verse
            poem = data.get("poem")
            order = data.get("order")
            if GanjoorVerse.objects.filter(poem=poem, order=order).exists():
                raise serializers.ValidationError(
                    _("A verse with this order already exists in this poem.")
                )
        return data


# -------------------
# Poem Serializers
# -------------------
class GanjoorPoemListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for poem list views."""

    poet_name = serializers.CharField(source="category.poet.name", read_only=True)
    category_title = serializers.CharField(source="category.title", read_only=True)
    verses_count = serializers.SerializerMethodField()

    class Meta:
        model = GanjoorPoem
        fields = [
            "id",
            "title",
            "url",
            "category",
            "category_title",
            "poet_name",
            "verses_count",
        ]
        read_only_fields = ["id"]

    def get_verses_count(self, obj):
        """Get number of verses in this poem."""
        return obj.verses.count()


class GanjoorPoemSerializer(serializers.ModelSerializer):
    """Detailed serializer for individual poem views with verses."""

    poet_name = serializers.CharField(source="category.poet.name", read_only=True)
    poet_id = serializers.IntegerField(source="category.poet.id", read_only=True)
    category_title = serializers.CharField(source="category.title", read_only=True)
    verses = GanjoorVerseSerializer(many=True, read_only=True)
    verses_count = serializers.SerializerMethodField()
    audios = serializers.SerializerMethodField()

    class Meta:
        model = GanjoorPoem
        fields = [
            "id",
            "title",
            "url",
            "category",
            "category_title",
            "poet_id",
            "poet_name",
            "verses",
            "verses_count",
            "audios",
        ]
        read_only_fields = ["id"]

    def get_verses_count(self, obj):
        """Get number of verses in this poem."""
        return obj.verses.count()

    def get_audios(self, obj):
        """Get audio files for this poem."""
        audios = obj.audios.filter(is_uploaded=True)
        return GanjoorPoemAudioSerializer(audios, many=True).data

    def validate_title(self, value):
        """Validate poem title is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError(_("Poem title cannot be empty."))
        return value.strip()


# -------------------
# Favorite Serializers
# -------------------
class GanjoorFavoriteSerializer(serializers.ModelSerializer):
    """Serializer for user favorites."""

    user_username = serializers.CharField(source="user.username", read_only=True)
    poem_title = serializers.CharField(source="poem.title", read_only=True)
    verse_text = serializers.CharField(source="verse.text", read_only=True)
    poet_name = serializers.CharField(source="poem.category.poet.name", read_only=True)

    class Meta:
        model = GanjoorFavorite
        fields = [
            "id",
            "user",
            "user_username",
            "poem",
            "poem_title",
            "verse",
            "verse_text",
            "poet_name",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at"]

    def validate(self, data):
        """Validate favorite doesn't already exist."""
        user = self.context["request"].user
        poem = data.get("poem")
        verse = data.get("verse")

        # Check if verse belongs to poem
        if verse.poem != poem:
            raise serializers.ValidationError(
                _("This verse does not belong to this poem.")
            )

        # Check for duplicates
        if GanjoorFavorite.objects.filter(user=user, poem=poem, verse=verse).exists():
            raise serializers.ValidationError(
                _("This verse has already been added to favorites.")
            )

        return data


# -------------------
# Audio Serializers
# -------------------
class GanjoorPoemAudioSerializer(serializers.ModelSerializer):
    """Serializer for poem audio files."""

    poem_title = serializers.CharField(source="poem.title", read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = GanjoorPoemAudio
        fields = [
            "id",
            "poem",
            "poem_title",
            "file",
            "file_url",
            "description",
            "download_url",
            "is_direct",
            "sync_guid",
            "file_checksum",
            "is_uploaded",
        ]
        read_only_fields = ["id", "file_checksum", "is_uploaded"]

    def get_file_url(self, obj):
        """Get absolute URL for audio file."""
        request = self.context.get("request")
        if obj.file and hasattr(obj.file, "url"):
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

    def validate_download_url(self, value):
        """Validate download URL format."""
        if not value.startswith(("http://", "https://")):
            raise serializers.ValidationError(
                _("Download URL must start with http:// or https://")
            )
        return value


class GanjoorAudioSyncSerializer(serializers.ModelSerializer):
    """Serializer for audio synchronization data."""

    poem_title = serializers.CharField(source="poem.title", read_only=True)
    verse_text = serializers.SerializerMethodField()

    class Meta:
        model = GanjoorAudioSync
        fields = [
            "id",
            "poem",
            "poem_title",
            "audio",
            "verse_order",
            "verse_text",
            "millisec",
        ]
        read_only_fields = ["id"]

    def get_verse_text(self, obj):
        """Get verse text for this sync point."""
        try:
            verse = obj.poem.verses.get(order=obj.verse_order)
            return verse.text
        except GanjoorVerse.DoesNotExist:
            return None

    def validate_verse_order(self, value):
        """Validate verse order is positive."""
        if value < 0:
            raise serializers.ValidationError(
                _("Verse order must be a positive number.")
            )
        return value

    def validate_millisec(self, value):
        """Validate milliseconds is positive."""
        if value < 0:
            raise serializers.ValidationError(_("Time must be a positive number."))
        return value

    def validate(self, data):
        """Validate audio belongs to poem and verse exists."""
        poem = data.get("poem")
        audio = data.get("audio")
        verse_order = data.get("verse_order")

        # Check if audio belongs to poem
        if audio.poem != poem:
            raise serializers.ValidationError(
                _("This audio file does not belong to this poem.")
            )

        # Check if verse exists in poem
        if not poem.verses.filter(order=verse_order).exists():
            raise serializers.ValidationError(
                _("A verse with this order does not exist in this poem.")
            )

        return data


# -------------------
# User Settings Serializer
# -------------------
class UserSettingSerializer(serializers.ModelSerializer):
    """Serializer for user settings."""

    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = UserSetting
        fields = [
            "id",
            "user",
            "username",
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
        read_only_fields = ["id", "user"]

    def validate_font_size(self, value):
        """Validate font size is within reasonable range."""
        if value < 8 or value > 48:
            raise serializers.ValidationError(_("Font size must be between 8 and 48."))
        return value

    def validate_view_mode(self, value):
        """Validate view mode is acceptable."""
        valid_modes = ["centered", "rtl", "ltr", "justified"]
        if value not in valid_modes:
            raise serializers.ValidationError(
                _("View mode must be one of: %(modes)s")
                % {"modes": ", ".join(valid_modes)}
            )
        return value
