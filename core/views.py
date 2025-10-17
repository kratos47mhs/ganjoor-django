from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from rest_framework import permissions, viewsets
from django.db.models import Q

from .models import (
    GanjoorAudioSync,
    GanjoorCategory,
    GanjoorFavorite,
    GanjoorPoem,
    GanjoorPoemAudio,
    GanjoorPoet,
    GanjoorVerse,
    UserSetting,
    VersePosition,
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


# -------------------
# Helper Functions
# -------------------
def get_breadcrumbs(category):
    """Return breadcrumbs safely even if parent category was deleted."""
    crumbs = []
    while category:
        crumbs.insert(0, category)
        try:
            category = category.parent  # may raise DoesNotExist
        except GanjoorCategory.DoesNotExist:
            break
    return crumbs



def get_all_poems(category):
    """Recursively collect all poems in category and subcategories."""
    poems = list(category.poems.select_related("category__poet").all())
    for subcat in category.children.all():
        poems += get_all_poems(subcat)
    return poems


# -------------------
# Regular Django Views
# -------------------
def home(request):
    poets_by_century = {}
    for century, century_display in GanjoorPoet.CENTURY_CHOICES:
        poets_by_century[century] = {
            'display': century_display,
            'poets': GanjoorPoet.objects.filter(century=century).order_by('name')
        }
    return render(request, "core/home.html", {"poets_by_century": poets_by_century})


def poet_detail(request, pk):
    poet = get_object_or_404(GanjoorPoet, pk=pk)
    categories = poet.categories.filter(parent=None)
    poems = GanjoorPoem.objects.select_related("category__poet").filter(category__poet=poet)
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
    category = get_object_or_404(GanjoorCategory.objects.select_related("poet"), pk=pk)
    poems = category.poems.select_related("category__poet").all()
    subcategories = category.children.all()
    breadcrumbs = get_breadcrumbs(category)
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
    # Fetch poem with category & poet to prevent N+1
    poem = get_object_or_404(
        GanjoorPoem.objects.select_related("category__poet"), pk=pk
    )

    # Group verses by order and position
    verses_qs = poem.verses.all().order_by("order", "position")
    verses_map = {}     # classic two-hemistich
    single_verses = []  # free, centered, comments, paragraphs

    for v in verses_qs:
        if v.position in (VersePosition.RIGHT, VersePosition.LEFT):
            if v.order not in verses_map:
                verses_map[v.order] = ["", ""]
            if v.position == VersePosition.RIGHT:
                verses_map[v.order][0] = v.text
            else:
                verses_map[v.order][1] = v.text
        else:
            single_verses.append(v)

    breadcrumbs = get_breadcrumbs(poem.category)

    return render(
        request,
        "core/poem_detail.html",
        {
            "poem": poem,
            "verses_map": verses_map,
            "single_verses": single_verses,
            "breadcrumbs": breadcrumbs,
        },
    )


@login_required
def favorites(request):
    favs = (
        request.user.ganjoor_favorites
        .select_related("poem__category__poet")
        .all()
    )
    return render(request, "core/favorites.html", {"favorites": favs})


def search(request):
    query = request.GET.get("q")
    if query:
        poems = GanjoorPoem.objects.search(query)
    else:
        poems = GanjoorPoem.objects.none()
    return render(
        request, "core/search_results.html", {"poems": poems, "query": query}
    )


# -------------------
# DRF ViewSets
# -------------------
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
    serializer_class = GanjoorFavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GanjoorFavorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


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
