from django.shortcuts import get_object_or_404, render
from rest_framework import permissions, viewsets

from . import serializers


# API endpoints
class GanjoorPoetViewSet(viewsets.ModelViewSet):
    queryset = serializers.GanjoorPoet.objects.all()
    serializer_class = serializers.GanjoorPoetSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class GanjoorCategoryViewSet(viewsets.ModelViewSet):
    queryset = serializers.GanjoorCategory.objects.all()
    serializer_class = serializers.GanjoorCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class GanjoorPoemViewSet(viewsets.ModelViewSet):
    queryset = serializers.GanjoorPoem.objects.all()
    serializer_class = serializers.GanjoorPoemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class GanjoorFavoriteViewSet(viewsets.ModelViewSet):
    queryset = serializers.GanjoorFavorite.objects.all()
    serializer_class = serializers.GanjoorFavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

class GanjoorVerseViewSet(viewsets.ModelViewSet):
    queryset = serializers.GanjoorVerse.objects.all()
    serializer_class = serializers.GanjoorVerseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class GanjoorPoemAudioViewSet(viewsets.ModelViewSet):
    queryset = serializers.GanjoorPoemAudio.objects.all()
    serializer_class = serializers.GanjoorPoemAudioSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class GanjoorAudioSyncViewSet(viewsets.ModelViewSet):
    queryset = serializers.GanjoorAudioSync.objects.all()
    serializer_class = serializers.GanjoorAudioSyncSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class UserSettingViewSet(viewsets.ModelViewSet):
    queryset = serializers.UserSetting.objects.all()
    serializer_class = serializers.UserSettingSerializer
    permission_classes = [permissions.IsAuthenticated]

# Web frontend views
def home(request):
    poets = serializers.GanjoorPoet.objects.all()
    return render(request, "core/home.html", {"poets": poets})

def poet_detail(request, pk):
    poet = get_object_or_404(serializers.GanjoorPoet, pk=pk)
    categories = poet.categories.all()
    return render(request, "core/poet_detail.html", {"poet": poet, "categories": categories})

def category_detail(request, pk):
    category = get_object_or_404(serializers.GanjoorCategory, pk=pk)
    poems = category.poems.all()
    return render(request, "core/category_detail.html", {"category": category, "poems": poems})

def poem_detail(request, pk):
    poem = get_object_or_404(serializers.GanjoorPoem, pk=pk)
    verses = poem.verses.all()
    return render(request, "core/poem_detail.html", {"poem": poem, "verses": verses})

def favorites(request):
    if request.user.is_authenticated:
        favs = request.user.ganjoor_favorites.select_related('poem').all()
    else:
        favs = []
    return render(request, "core/favorites.html", {"favorites": favs})