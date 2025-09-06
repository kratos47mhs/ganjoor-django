from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q

# === Best Practices Model Implementation ===
# - Use snake_case for field names unless mapped to legacy db
# - Clarify related_name, blank/null usage, and constraints
# - Prefer FileField/ImageField where possible for files
# - Add docstrings for each model
# - Prefer explicit db_table only for legacy compatibility
# - Avoid ambiguous fields (e.g., 'pos', 'curver'), use descriptive names
# - Group related models and order logically
# - Annotate each class with recommended practices where relevant

class GanjoorCategory(models.Model):
    """
    Represents a category (e.g., book, chapter) under a poet.
    Supports hierarchical nesting via parent.
    """
    poet = models.ForeignKey(
        'GanjoorPoet', on_delete=models.CASCADE, related_name='categories'
    )
    title = models.CharField(max_length=255, blank=True, null=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='children'
    )
    url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'ganjoor_category'
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title or f"Category {self.pk}"


class GanjoorPoet(models.Model):
    """
    Represents a poet in the Ganjoor database.
    """
    name = models.CharField(max_length=255, db_index=True)
    category = models.ForeignKey(
        GanjoorCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='poets'
    )
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'ganjoor_poet'
        verbose_name = "Poet"
        verbose_name_plural = "Poets"

    def __str__(self):
        return self.name


class GanjoorPoemQuerySet(models.QuerySet):
    """
    Custom QuerySet with a full-text search helper.
    """
    def search(self, query, poet_id=None):
        qs = self
        if poet_id:
            qs = qs.filter(category__poet_id=poet_id)
        return qs.filter(Q(title__icontains=query) | Q(verses__text__icontains=query)).distinct()


class GanjoorPoem(models.Model):
    """
    Represents a poem, belonging to a category.
    """
    category = models.ForeignKey(
        GanjoorCategory, on_delete=models.CASCADE, related_name='poems'
    )
    title = models.CharField(max_length=255, db_index=True)
    url = models.CharField(max_length=255)
    # Use custom queryset for search functionality
    objects = GanjoorPoemQuerySet.as_manager()

    class Meta:
        db_table = 'ganjoor_poem'
        verbose_name = "Poem"
        verbose_name_plural = "Poems"

    def __str__(self):
        return self.title


class GanjoorVerse(models.Model):
    """
    Represents a verse (bayt) in a poem.
    """
    poem = models.ForeignKey(
        GanjoorPoem, on_delete=models.CASCADE, related_name='verses'
    )
    order = models.PositiveIntegerField(help_text="Order of the verse in the poem")
    position = models.PositiveIntegerField(help_text="Position within a structure (e.g., line, stanza)")
    text = models.TextField()

    class Meta:
        db_table = 'ganjoor_verse'
        constraints = [
            models.UniqueConstraint(
                fields=['order', 'poem'], name='unique_verse_per_poem'
            )
        ]
        ordering = ['order']

    def __str__(self):
        return f"{self.poem.title} [{self.order}]"


class GanjoorFavorite(models.Model):
    """
    User's favorite verse in a poem.
    """
    user = models.ForeignKey(User, related_name='ganjoor_favorites', on_delete=models.CASCADE)
    poem = models.ForeignKey(GanjoorPoem, on_delete=models.CASCADE)
    verse = models.ForeignKey(GanjoorVerse, on_delete=models.CASCADE)
    verse_position = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ganjoor_favorite'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'poem'], name='unique_user_poem_fav'
            )
        ]

    def __str__(self):
        return f"{self.user.username} → {self.poem.title}"


class GanjoorPoemAudio(models.Model):
    """
    Audio file associated with a poem.
    """
    poem = models.ForeignKey(
        GanjoorPoem, on_delete=models.CASCADE, related_name='audios'
    )
    file = models.FileField(upload_to='poem_audios/')
    description = models.TextField(blank=True)
    download_url = models.URLField(max_length=500)
    is_direct = models.BooleanField(default=False)
    sync_guid = models.CharField(max_length=255)
    file_checksum = models.CharField(max_length=255)
    is_uploaded = models.BooleanField(default=False)

    class Meta:
        db_table = 'ganjoor_poem_audio'
        verbose_name = "Poem Audio"
        verbose_name_plural = "Poem Audios"

    def __str__(self):
        return f"Audio for {self.poem.title}"


class GanjoorAudioSync(models.Model):
    """
    Synchronization between audio and verses.
    """
    poem = models.ForeignKey(GanjoorPoem, on_delete=models.CASCADE)
    audio = models.ForeignKey(GanjoorPoemAudio, on_delete=models.CASCADE)
    verse_order = models.PositiveIntegerField()
    millisec = models.PositiveIntegerField()

    class Meta:
        db_table = 'ganjoor_audio_sync'
        verbose_name = "Audio Sync"
        verbose_name_plural = "Audio Syncs"

    def __str__(self):
        return f"Sync {self.poem.title} @ {self.verse_order}"


class UserSetting(models.Model):
    """
    User-specific configuration for viewing poems.
    Consider moving to a JSONField if settings grow.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="ganjoor_settings")
    view_mode = models.CharField(max_length=50, default="centered")
    font_size = models.FloatField(default=16)
    show_line_numbers = models.BooleanField(default=True)
    last_highlight = models.CharField(max_length=255, blank=True, null=True)
    browse_button_visible = models.BooleanField(default=True)
    comments_button_visible = models.BooleanField(default=True)
    copy_button_visible = models.BooleanField(default=True)
    print_button_visible = models.BooleanField(default=True)
    home_button_visible = models.BooleanField(default=True)
    random_button_visible = models.BooleanField(default=True)
    editor_button_visible = models.BooleanField(default=True)
    download_button_visible = models.BooleanField(default=True)

    class Meta:
        verbose_name = "User Setting"
        verbose_name_plural = "User Settings"

    def __str__(self):
        return f"Settings for {self.user.username}"

# ---- Deprecated/Legacy Models (should document usage or refactor) ----

class Gil(models.Model):
    """
    Legacy audio segment pointer. Consider refactoring or removing.
    """
    category = models.ForeignKey(GanjoorCategory, on_delete=models.CASCADE)

    class Meta:
        db_table = "gil"

    def __str__(self):
        return f"Gil {self.pk}"


class Gver(models.Model):
    """
    Legacy version pointer. Consider refactoring or removing.
    """
    current_version = models.PositiveIntegerField()

    class Meta:
        db_table = "gver"

    def __str__(self):
        return f"Version {self.current_version}"