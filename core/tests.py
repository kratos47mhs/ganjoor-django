from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import GanjoorPoet, GanjoorCategory, GanjoorPoem, GanjoorVerse

User = get_user_model()

class GanjoorPoetModelTest(TestCase):
    def setUp(self):
        self.poet = GanjoorPoet.objects.create(name="Hafez")

    def test_str(self):
        self.assertEqual(str(self.poet), "Hafez")

class GanjoorCategoryModelTest(TestCase):
    def setUp(self):
        self.poet = GanjoorPoet.objects.create(name="Saadi")
        self.category = GanjoorCategory.objects.create(poet=self.poet, title="Ghazals")

    def test_str(self):
        self.assertEqual(str(self.category), "Ghazals")

class GanjoorPoemModelTest(TestCase):
    def setUp(self):
        self.poet = GanjoorPoet.objects.create(name="Rumi")
        self.category = GanjoorCategory.objects.create(poet=self.poet, title="Masnavi")
        self.poem = GanjoorPoem.objects.create(category=self.category, title="First Poem", url="poem-1")

    def test_str(self):
        self.assertEqual(str(self.poem), "First Poem")

class GanjoorVerseModelTest(TestCase):
    def setUp(self):
        self.poet = GanjoorPoet.objects.create(name="Attar")
        self.category = GanjoorCategory.objects.create(poet=self.poet, title="Divan")
        self.poem = GanjoorPoem.objects.create(category=self.category, title="Divan Poem", url="divan-poem")
        self.verse = GanjoorVerse.objects.create(poem=self.poem, order=1, position=1, text="Some verse text")

    def test_str(self):
        self.assertIn("Divan Poem", str(self.verse))