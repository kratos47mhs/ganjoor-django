from django.db import models


class GanjoorPoet(models.Model):
    """Poet"""

    id = models.AutoField(primary_key=True, db_column="id")
    name = models.CharField("نام شاعر", max_length=255, db_column="name")
    bio = models.TextField("زندگینامه یا توضیحات", blank=True, db_column="description")

    class Meta:
        db_table = "poet"
        verbose_name = "Poet"
        verbose_name_plural = "Poets"

    def __str__(self):
        return self.name


class GanjoorCat(models.Model):
    """Category/Section"""

    id = models.AutoField(primary_key=True, db_column="id")
    poet = models.ForeignKey(
        GanjoorPoet,
        on_delete=models.CASCADE,
        related_name="categories",
        db_column="poet_id",
        help_text="شاعر مرتبط",
    )
    text = models.CharField("عنوان بخش", max_length=255, db_column="text")
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="parent_id",
        related_name="children",
        help_text="بخش والد",
    )
    url = models.URLField("نشانی بخش", max_length=500, db_column="url")

    class Meta:
        db_table = "cat"
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.text


class GanjoorPoem(models.Model):
    """Poem"""

    id = models.AutoField(primary_key=True, db_column="id")
    cat = models.ForeignKey(
        GanjoorCat,
        on_delete=models.CASCADE,
        related_name="poems",
        db_column="cat_id",
        help_text="بخشی که شعر به آن تعلق دارد",
    )
    title = models.CharField("عنوان شعر", max_length=255, db_column="title")
    url = models.URLField("نشانی شعر", max_length=500, db_column="url")

    class Meta:
        db_table = "poem"
        verbose_name = "Poem"
        verbose_name_plural = "Poems"

    def __str__(self):
        return self.title


class VersePosition(models.IntegerChoices):
    RIGHT = 0, "Right (مصرع اول)"
    LEFT = 1, "Left (مصرع دوم)"
    CENTERED_VERSE1 = 2, "Centered Verse 1 (مصرع اول/تنها)"
    CENTERED_VERSE2 = 3, "Centered Verse 2 (مصرع دوم)"
    SINGLE = 4, "Single (مصرع آزاد/نیمایی)"
    COMMENT = 5, "Comment (توضیح)"
    PARAGRAPH = -1, "Paragraph (نثر)"


class GanjoorVerse(models.Model):
    """Verse"""

    id = models.AutoField(primary_key=True, db_column="id")
    poem = models.ForeignKey(
        GanjoorPoem,
        on_delete=models.CASCADE,
        related_name="verses",
        db_column="poem_id",
        help_text="شعر مرتبط",
    )
    vorder = models.PositiveIntegerField("ترتیب مصرع", db_column="vorder")
    position = models.IntegerField(
        "نوع و جایگاه مصرع", choices=VersePosition.choices, db_column="position"
    )
    text = models.TextField("متن مصرع", db_column="text")

    class Meta:
        db_table = "verse"
        verbose_name = "Verse"
        verbose_name_plural = "Verses"
        unique_together = ("poem", "vorder")

    def __str__(self):
        return self.text
