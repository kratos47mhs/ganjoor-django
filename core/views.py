from rest_framework import viewsets, permissions
from django.shortcuts import render, get_object_or_404
from .models import (
    GanjoorPoet,
    GanjoorCategory,
    GanjoorPoem,
    GanjoorVerse,
    GanjoorFavorite,
    GanjoorPoemAudio,
    GanjoorAudioSync,
    UserSetting,
)
from .serializers import (
    GanjoorPoetSerializer,
    GanjoorCategorySerializer,
    GanjoorPoemSerializer,
    GanjoorVerseSerializer,
    GanjoorFavoriteSerializer,
    GanjoorPoemAudioSerializer,
    GanjoorAudioSyncSerializer,
    UserSettingSerializer,
)

# --- API ViewSets ---

class GanjoorPoetViewSet(viewsets.ModelViewSet):
    queryset = GanjoorPoet.objects.all()
    serializer_class = GanjoorPoetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class GanjoorCategoryViewSet(viewsets.ModelViewSet):
    queryset = GanjoorCategory.objects.all()
    serializer_class = GanjoorCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class GanjoorPoemViewSet(viewsets.ModelViewSet):
    queryset = GanjoorPoem.objects.all()
    serializer_class = GanjoorPoemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class GanjoorFavoriteViewSet(viewsets.ModelViewSet):
    queryset = GanjoorFavorite.objects.all()
    serializer_class = GanjoorFavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

class GanjoorVerseViewSet(viewsets.ModelViewSet):
    queryset = GanjoorVerse.objects.all()
    serializer_class = GanjoorVerseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class GanjoorPoemAudioViewSet(viewsets.ModelViewSet):
    queryset = GanjoorPoemAudio.objects.all()
    serializer_class = GanjoorPoemAudioSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class GanjoorAudioSyncViewSet(viewsets.ModelViewSet):
    queryset = GanjoorAudioSync.objects.all()
    serializer_class = GanjoorAudioSyncSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class UserSettingViewSet(viewsets.ModelViewSet):
    queryset = UserSetting.objects.all()
    serializer_class = UserSettingSerializer
    permission_classes = [permissions.IsAuthenticated]

# --- Web (HTML) Views ---

def home(request):
    poets = GanjoorPoet.objects.all()
    return render(request, "core/home.html", {"poets": poets})

def poet_detail(request, pk):
    poet = get_object_or_404(GanjoorPoet, pk=pk)
    categories = poet.categories.all()
    return render(request, "core/poet_detail.html", {"poet": poet, "categories": categories})

def category_detail(request, pk):
    category = get_object_or_404(GanjoorCategory, pk=pk)
    poems = category.poems.all()
    return render(request, "core/category_detail.html", {"category": category, "poems": poems})

def poem_detail(request, pk):
    poem = get_object_or_404(GanjoorPoem, pk=pk)
    verses = poem.verses.all()
    return render(request, "core/poem_detail.html", {"poem": poem, "verses": verses})

def favorites(request):
    if request.user.is_authenticated:
        favs = request.user.ganjoor_favorites.select_related('poem').all()
    else:
        favs = []
    return render(request, "core/favorites.html", {"favorites": favs})