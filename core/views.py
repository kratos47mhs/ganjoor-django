from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from rest_framework import permissions, viewsets

from .models import (
    GanjoorAudioSync,
    GanjoorCategory,
    GanjoorFavorite,
    GanjoorPoem,
    GanjoorPoemAudio,
    GanjoorPoet,
    GanjoorVerse,
    UserSetting,
)
from .serializers import (
    GanjoorAudioSyncSerializer,
    GanjoorCategorySerializer,
    GanjoorFavoriteSerializer,
    GanjoorPoemAudioSerializer,
    GanjoorPoemSerializer,
    GanjoorPoetSerializer,
    GanjoorVerseSerializer,
    UserSettingSerializer,
)


def home(request):
    poets = GanjoorPoet.objects.all()
    return render(request, "core/home.html", {"poets": poets})


def poet_detail(request, pk):
    poet = get_object_or_404(GanjoorPoet, pk=pk)
    categories = poet.categories.filter(parent=None)
    poems = GanjoorPoem.objects.filter(category__poet=poet)
    return render(
        request,
        "core/poet_detail.html",
        {
            "poet": poet,
            "categories": categories,
            "poems": poems,
        },
    )


def category_detail(request, pk):
    category = get_object_or_404(GanjoorCategory, pk=pk)
    poems = category.poems.all()
    subcategories = category.children.all()

    # Safe breadcrumbs
    breadcrumbs = []
    cat = category
    while cat:
        breadcrumbs.insert(0, cat)
        if cat.parent_id is None:
            break
        try:
            cat = GanjoorCategory.objects.get(pk=cat.parent_id)
        except GanjoorCategory.DoesNotExist:
            break

    # Recursively collect all poems in subcategories
    def get_all_poems(cat):
        poems = list(cat.poems.all())
        for subcat in cat.children.all():
            poems += get_all_poems(subcat)
        return poems

    all_poems = get_all_poems(category)

    return render(
        request,
        "core/category_detail.html",
        {
            "category": category,
            "poems": poems,
            "all_poems": all_poems,
            "subcategories": subcategories,
            "breadcrumbs": breadcrumbs,
        },
    )


def poem_detail(request, pk):
    poem = get_object_or_404(GanjoorPoem, pk=pk)
    verses = poem.verses.all()
    breadcrumbs = []
    cat = poem.category
    while cat:
        breadcrumbs.insert(0, cat)
        if cat.parent_id is None:
            break
        # fetch parent by id, or break if not found
        try:
            cat = GanjoorCategory.objects.get(pk=cat.parent_id)
        except GanjoorCategory.DoesNotExist:
            break
    return render(
        request,
        "core/poem_detail.html",
        {
            "poem": poem,
            "verses": verses,
            "breadcrumbs": breadcrumbs,
        },
    )


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


class GanjoorVerseViewSet(viewsets.ModelViewSet):
    queryset = GanjoorVerse.objects.all()
    serializer_class = GanjoorVerseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class GanjoorFavoriteViewSet(viewsets.ModelViewSet):
    queryset = GanjoorFavorite.objects.all()
    serializer_class = GanjoorFavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]


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


@login_required
def favorites(request):
    favs = request.user.ganjoor_favorites.select_related("poem").all()
    return render(request, "core/favorites.html", {"favorites": favs})
