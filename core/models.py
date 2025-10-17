from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from django.core.validators import URLValidator


# -------------------
# Poet
# -------------------
class GanjoorPoet(models.Model):
    CENTURY_CHOICES = [
        ('ancient', 'باستانی'),
        ('classical', 'کلاسیک'),
        ('contemporary', 'معاصر'),
        ('modern', 'نو'),
    ]
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    century = models.CharField(max_length=20, choices=CENTURY_CHOICES, default='classical', db_index=True)
    image = models.ImageField(upload_to='poets/', blank=True, null=True, help_text='Portrait image of the poet')
    image_slug = models.CharField(max_length=255, blank=True, null=True, help_text='English transliteration for image filename')

    class Meta:
        db_table = "ganjoor_poet"
        verbose_name = "Poet"
        verbose_name_plural = "Poets"

    def __str__(self):
        return self.name


# -------------------
# Category
# -------------------
class GanjoorCategory(models.Model):
    poet = models.ForeignKey(
        GanjoorPoet, on_delete=models.CASCADE, related_name="categories"
    )
    title = models.CharField(max_length=255, db_index=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "ganjoor_category"
        verbose_name = "Category"
        verbose_name_plural = "Categories"

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
        GanjoorCategory, on_delete=models.CASCADE, related_name="poems"
    )
    title = models.CharField(max_length=255, db_index=True)
    url = models.CharField(max_length=255, db_index=True)

    objects = GanjoorPoemQuerySet.as_manager()

    class Meta:
        db_table = "ganjoor_poem"
        verbose_name = "Poem"
        verbose_name_plural = "Poems"

    def __str__(self):
        return self.title


# -------------------
# Verse Position Enum
# -------------------
class VersePosition(models.IntegerChoices):
    RIGHT = 0, "Right (مصرع اول)"
    LEFT = 1, "Left (مصرع دوم)"
    CENTERED_VERSE1 = 2, "Centered Verse 1 (ترجیع/ترکیب)"
    CENTERED_VERSE2 = 3, "Centered Verse 2 (ترجیع/ترکیب)"
    SINGLE = 4, "Single (نیمایی/آزاد)"
    COMMENT = 5, "Comment (توضیح)"
    PARAGRAPH = -1, "Paragraph (نثر)"


# -------------------
# Verse
# -------------------
class GanjoorVerse(models.Model):
    poem = models.ForeignKey(
        GanjoorPoem, on_delete=models.CASCADE, related_name="verses"
    )
    order = models.PositiveIntegerField(
        help_text="Order of the verse in the poem", db_index=True
    )
    position = models.SmallIntegerField(
        choices=VersePosition.choices, default=VersePosition.RIGHT
    )
    text = models.TextField()

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
        User, related_name="ganjoor_favorites", on_delete=models.CASCADE, db_index=True
    )
    poem = models.ForeignKey(
        GanjoorPoem, on_delete=models.CASCADE, related_name="favorites"
    )
    verse = models.ForeignKey(
        GanjoorVerse, on_delete=models.CASCADE, related_name="favorites"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ganjoor_favorite"
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
        GanjoorPoem, on_delete=models.CASCADE, related_name="audios"
    )
    file = models.FileField(upload_to="poem_audios/")
    description = models.TextField(blank=True, null=True)
    download_url = models.URLField(max_length=500)
    is_direct = models.BooleanField(default=False)
    sync_guid = models.CharField(max_length=255, db_index=True)
    file_checksum = models.CharField(max_length=255)
    is_uploaded = models.BooleanField(default=False)

    class Meta:
        db_table = "ganjoor_poem_audio"
        verbose_name = "Poem Audio"
        verbose_name_plural = "Poem Audios"

    def __str__(self):
        return f"Audio for {self.poem.title}"


# -------------------
# Audio Sync
# -------------------
class GanjoorAudioSync(models.Model):
    poem = models.ForeignKey(
        GanjoorPoem, on_delete=models.CASCADE, related_name="audio_syncs"
    )
    audio = models.ForeignKey(
        GanjoorPoemAudio, on_delete=models.CASCADE, related_name="syncs"
    )
    verse_order = models.PositiveIntegerField()
    millisec = models.PositiveIntegerField()

    class Meta:
        db_table = "ganjoor_audio_sync"
        verbose_name = "Audio Sync"
        verbose_name_plural = "Audio Syncs"

    def __str__(self):
        return f"Sync {self.poem.title} @ {self.verse_order}"


# -------------------
# User Setting
# -------------------
class UserSetting(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="ganjoor_settings"
    )
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
