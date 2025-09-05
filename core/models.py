from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q


class GanjoorPoet(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    bio = models.TextField(blank=True)
    birth_year = models.IntegerField(blank=True, null=True)
    death_year = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name


class GanjoorCat(models.Model):
    poet = models.ForeignKey(
        GanjoorPoet, on_delete=models.CASCADE, related_name="categories"
    )
    text = models.CharField(max_length=255)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="children"
    )
    url = models.URLField(max_length=500, unique=True)
    start_poem = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.text


class GanjoorPoem(models.Model):
    poet = models.ForeignKey(
        GanjoorPoet, related_name="poems", on_delete=models.CASCADE
    )
    category = models.ForeignKey(
        GanjoorCat, on_delete=models.CASCADE, related_name="poems"
    )
    text = models.TextField()
    has_comments = models.BooleanField(default=False)
    gdb_id = models.IntegerField(blank=True, null=True)  # For imported DBs
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255)
    url = models.URLField(max_length=500, unique=True)
    highlight_text = models.TextField(blank=True, null=True)

    # Many-to-Many through favorites
    favorited_by = models.ManyToManyField(
        User, through="GanjoorFavorite", related_name="favorite_poems"
    )

    def __str__(self):
        return self.title


class VersePosition(models.IntegerChoices):
    RIGHT = 0, "Right (first hemistich)"
    LEFT = 1, "Left (second hemistich)"
    CENTERED1 = 2, "Centered verse part 1"
    CENTERED2 = 3, "Centered verse part 2"
    SINGLE = 4, "Single line"
    COMMENT = 5, "Comment"
    PARAGRAPH = -1, "Paragraph"


class GanjoorVerse(models.Model):
    poem = models.ForeignKey(
        GanjoorPoem, on_delete=models.CASCADE, related_name="verses"
    )
    order = models.PositiveIntegerField()
    position = models.IntegerField(
        choices=VersePosition.choices, default=VersePosition.RIGHT
    )
    text = models.TextField()

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.text[:50]


class GanjoorFavorite(models.Model):
    user = models.ForeignKey(User, related_name="favorites", on_delete=models.CASCADE)
    poem = models.ForeignKey(GanjoorPoem, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "poem")


class GanjoorPoemAudio(models.Model):
    poem = models.ForeignKey(
        GanjoorPoem, related_name="audio_files", on_delete=models.CASCADE
    )
    file = models.FileField(upload_to="poem_audio/")
    narrator = models.CharField(max_length=255, blank=True, null=True)
    duration_seconds = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"Audio for {self.poem.title}"


class UserSetting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    view_mode = models.CharField(max_length=50, default="centered")  # centered / normal
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


def search_poems(query: str, poet_id: int = None):
    poems = GanjoorPoem.objects.all()
    if poet_id:
        poems = poems.filter(poet_id=poet_id)
    return poems.filter(Q(title__icontains=query) | Q(text__icontains=query))
