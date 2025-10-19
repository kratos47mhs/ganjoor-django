from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


# -------------------
# Poet
# -------------------
class GanjoorPoet(models.Model):
    CENTURY_CHOICES = [
        ("ancient", _("Ancient")),
        ("classical", _("Classical")),
        ("contemporary", _("Contemporary")),
        ("modern", _("Modern")),
    ]
    name = models.CharField(max_length=255, db_index=True, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    century = models.CharField(
        max_length=20,
        choices=CENTURY_CHOICES,
        default="classical",
        db_index=True,
        verbose_name=_("Century"),
    )
    image = models.ImageField(
        upload_to="poets/",
        blank=True,
        null=True,
        help_text=_("Portrait image of the poet"),
        verbose_name=_("Image"),
    )
    image_slug = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_("English transliteration for image filename"),
        verbose_name=_("Image Slug"),
    )

    class Meta:
        db_table = "ganjoor_poet"
        verbose_name = _("Poet")
        verbose_name_plural = _("Poets")

    def __str__(self):
        return self.name


# -------------------
# Category
# -------------------
class GanjoorCategory(models.Model):
    poet = models.ForeignKey(
        GanjoorPoet,
        on_delete=models.CASCADE,
        related_name="categories",
        verbose_name=_("Poet"),
    )
    title = models.CharField(max_length=255, db_index=True, verbose_name=_("Title"))
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name=_("Parent Category"),
    )
    url = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("URL"))

    class Meta:
        db_table = "ganjoor_category"
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.title


# -------------------
# Poem QuerySet
# -------------------
class GanjoorPoemQuerySet(models.QuerySet):
    def search(self, query, poet_id=None):
        qs = self
        if poet_id:
            qs = qs.filter(category__poet_id=poet_id)
        return qs.filter(
            Q(title__icontains=query) | Q(verses__text__icontains=query)
        ).distinct()


# -------------------
# Poem
# -------------------
class GanjoorPoem(models.Model):
    category = models.ForeignKey(
        GanjoorCategory,
        on_delete=models.CASCADE,
        related_name="poems",
        verbose_name=_("Category"),
    )
    title = models.CharField(max_length=255, db_index=True, verbose_name=_("Title"))
    url = models.CharField(max_length=255, db_index=True, verbose_name=_("URL"))

    objects = GanjoorPoemQuerySet.as_manager()

    class Meta:
        db_table = "ganjoor_poem"
        verbose_name = _("Poem")
        verbose_name_plural = _("Poems")

    def __str__(self):
        return self.title


# -------------------
# Verse Position Enum
# -------------------
class VersePosition(models.IntegerChoices):
    RIGHT = 0, _("Right (First Hemistich)")
    LEFT = 1, _("Left (Second Hemistich)")
    CENTERED_VERSE1 = 2, _("Centered Verse 1")
    CENTERED_VERSE2 = 3, _("Centered Verse 2")
    SINGLE = 4, _("Single (Free Verse)")
    COMMENT = 5, _("Comment")
    PARAGRAPH = -1, _("Paragraph (Prose)")


# -------------------
# Verse
# -------------------
class GanjoorVerse(models.Model):
    poem = models.ForeignKey(
        GanjoorPoem,
        on_delete=models.CASCADE,
        related_name="verses",
        verbose_name=_("Poem"),
    )
    order = models.PositiveIntegerField(
        help_text=_("Order of the verse in the poem"),
        db_index=True,
        verbose_name=_("Order"),
    )
    position = models.SmallIntegerField(
        choices=VersePosition.choices,
        default=VersePosition.RIGHT,
        verbose_name=_("Position"),
    )
    text = models.TextField(verbose_name=_("Text"))

    class Meta:
        db_table = "ganjoor_verse"
        constraints = [
            models.UniqueConstraint(
                fields=["order", "poem"], name="unique_verse_per_poem"
            )
        ]
        ordering = ["order"]

    def __str__(self):
        return f"{self.poem.title} [{self.order}] {self.text[:20]}..."


# -------------------
# Favorite
# -------------------
class GanjoorFavorite(models.Model):
    user = models.ForeignKey(
        User,
        related_name="ganjoor_favorites",
        on_delete=models.CASCADE,
        db_index=True,
        verbose_name=_("User"),
    )
    poem = models.ForeignKey(
        GanjoorPoem,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name=_("Poem"),
    )
    verse = models.ForeignKey(
        GanjoorVerse,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name=_("Verse"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        db_table = "ganjoor_favorite"
        verbose_name = _("Favorite")
        verbose_name_plural = _("Favorites")
        constraints = [
            models.UniqueConstraint(
                fields=["user", "poem", "verse"], name="unique_user_poem_verse_fav"
            )
        ]

    def __str__(self):
        return f"{self.user.username} → {self.poem.title}"


# -------------------
# Poem Audio
# -------------------
class GanjoorPoemAudio(models.Model):
    poem = models.ForeignKey(
        GanjoorPoem,
        on_delete=models.CASCADE,
        related_name="audios",
        verbose_name=_("Poem"),
    )
    file = models.FileField(upload_to="poem_audios/", verbose_name=_("Audio File"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    download_url = models.URLField(max_length=500, verbose_name=_("Download URL"))
    is_direct = models.BooleanField(default=False, verbose_name=_("Is Direct"))
    sync_guid = models.CharField(
        max_length=255, db_index=True, verbose_name=_("Sync GUID")
    )
    file_checksum = models.CharField(max_length=255, verbose_name=_("File Checksum"))
    is_uploaded = models.BooleanField(default=False, verbose_name=_("Is Uploaded"))

    class Meta:
        db_table = "ganjoor_poem_audio"
        verbose_name = _("Poem Audio")
        verbose_name_plural = _("Poem Audios")

    def __str__(self):
        return f"Audio for {self.poem.title}"


# -------------------
# Audio Sync
# -------------------
class GanjoorAudioSync(models.Model):
    poem = models.ForeignKey(
        GanjoorPoem,
        on_delete=models.CASCADE,
        related_name="audio_syncs",
        verbose_name=_("Poem"),
    )
    audio = models.ForeignKey(
        GanjoorPoemAudio,
        on_delete=models.CASCADE,
        related_name="syncs",
        verbose_name=_("Audio"),
    )
    verse_order = models.PositiveIntegerField(verbose_name=_("Verse Order"))
    millisec = models.PositiveIntegerField(verbose_name=_("Milliseconds"))

    class Meta:
        db_table = "ganjoor_audio_sync"
        verbose_name = _("Audio Sync")
        verbose_name_plural = _("Audio Syncs")

    def __str__(self):
        return f"Sync {self.poem.title} @ {self.verse_order}"


# -------------------
# User Setting
# -------------------
class UserSetting(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="ganjoor_settings",
        verbose_name=_("User"),
    )
    view_mode = models.CharField(
        max_length=50, default="centered", verbose_name=_("View Mode")
    )
    font_size = models.FloatField(default=16, verbose_name=_("Font Size"))
    show_line_numbers = models.BooleanField(
        default=True, verbose_name=_("Show Line Numbers")
    )
    last_highlight = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_("Last Highlight")
    )
    browse_button_visible = models.BooleanField(
        default=True, verbose_name=_("Browse Button Visible")
    )
    comments_button_visible = models.BooleanField(
        default=True, verbose_name=_("Comments Button Visible")
    )
    copy_button_visible = models.BooleanField(
        default=True, verbose_name=_("Copy Button Visible")
    )
    print_button_visible = models.BooleanField(
        default=True, verbose_name=_("Print Button Visible")
    )
    home_button_visible = models.BooleanField(
        default=True, verbose_name=_("Home Button Visible")
    )
    random_button_visible = models.BooleanField(
        default=True, verbose_name=_("Random Button Visible")
    )
    editor_button_visible = models.BooleanField(
        default=True, verbose_name=_("Editor Button Visible")
    )
    download_button_visible = models.BooleanField(
        default=True, verbose_name=_("Download Button Visible")
    )

    class Meta:
        verbose_name = _("User Setting")
        verbose_name_plural = _("User Settings")

    def __str__(self):
        return f"Settings for {self.user.username}"
