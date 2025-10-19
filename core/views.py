"""
Views for the Ganjoor application.

This module contains both traditional Django views for web pages
and DRF ViewSets for the REST API.
"""

import logging
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.db.models import Q, Prefetch, Count
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.translation import gettext_lazy as _
from django.utils.translation import get_language
from rest_framework import permissions, viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

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
    GanjoorCategoryListSerializer,
    GanjoorFavoriteSerializer,
    GanjoorPoemAudioSerializer,
    GanjoorPoemSerializer,
    GanjoorPoemListSerializer,
    GanjoorPoetSerializer,
    GanjoorPoetListSerializer,
    GanjoorVerseSerializer,
    UserSettingSerializer,
)

logger = logging.getLogger(__name__)


# -------------------
# Helper Functions
# -------------------
def get_breadcrumbs(category):
    """
    Return breadcrumbs safely even if parent category was deleted.

    Args:
        category: GanjoorCategory instance

    Returns:
        List of category objects representing the breadcrumb trail
    """
    crumbs = []
    current = category
    max_depth = 10  # Prevent infinite loops
    depth = 0

    while current and depth < max_depth:
        crumbs.insert(0, current)
        try:
            current = current.parent
        except GanjoorCategory.DoesNotExist:
            break
        depth += 1

    return crumbs


def get_all_poems(category):
    """
    Recursively collect all poems in category and subcategories.

    Args:
        category: GanjoorCategory instance

    Returns:
        List of GanjoorPoem objects
    """
    poems = list(category.poems.select_related("category__poet").all())
    for subcat in category.children.all():
        poems += get_all_poems(subcat)
    return poems


# -------------------
# Regular Django Views
# -------------------
@cache_page(60 * 15)  # Cache for 15 minutes
def home(request):
    """
    Display the home page with poets grouped by century.

    Args:
        request: HTTP request object

    Returns:
        Rendered home page
    """
    poets_by_century = {}

    for century, century_display in GanjoorPoet.CENTURY_CHOICES:
        poets = GanjoorPoet.objects.filter(century=century).order_by("name")
        if poets.exists():
            poets_by_century[century] = {"display": century_display, "poets": poets}

    return render(request, "core/home.html", {"poets_by_century": poets_by_century})


def poet_detail(request, pk):
    """
    Display poet detail page with categories and poems.

    Args:
        request: HTTP request object
        pk: Primary key of the poet

    Returns:
        Rendered poet detail page
    """
    # Use select_related and prefetch_related for optimization
    poet = get_object_or_404(GanjoorPoet, pk=pk)

    # Get top-level categories with poem counts
    categories = (
        poet.categories.filter(parent=None)
        .prefetch_related("children")
        .annotate(poems_count=Count("poems"))
        .order_by("title")
    )

    # Get all poems for this poet
    poems = (
        GanjoorPoem.objects.select_related("category__poet")
        .filter(category__poet=poet)
        .order_by("title")[:50]  # Limit initial display
    )

    context = {
        "poet": poet,
        "categories": categories,
        "poems": poems,
    }

    return render(request, "core/poet_detail.html", context)


def category_detail(request, pk):
    """
    Display category detail page with poems and subcategories.

    Args:
        request: HTTP request object
        pk: Primary key of the category

    Returns:
        Rendered category detail page
    """
    # Optimize query with select_related
    category = get_object_or_404(
        GanjoorCategory.objects.select_related("poet", "parent"), pk=pk
    )

    # Get poems in this category
    poems = category.poems.select_related("category__poet").order_by("title")

    # Get subcategories with poem counts
    subcategories = category.children.annotate(poems_count=Count("poems")).order_by(
        "title"
    )

    breadcrumbs = get_breadcrumbs(category)
    all_poems = get_all_poems(category)

    context = {
        "category": category,
        "poems": poems,
        "all_poems": all_poems,
        "subcategories": subcategories,
        "breadcrumbs": breadcrumbs,
    }

    return render(request, "core/category_detail.html", context)


def poem_detail(request, pk):
    """
    Display poem detail page with verses.

    Args:
        request: HTTP request object
        pk: Primary key of the poem

    Returns:
        Rendered poem detail page
    """
    # Fetch poem with category & poet to prevent N+1
    poem = get_object_or_404(
        GanjoorPoem.objects.select_related("category__poet"), pk=pk
    )

    # Group verses by order and position
    verses_qs = poem.verses.all().order_by("order", "position")
    verses_map = {}  # classic two-hemistich
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

    # Get audio files for this poem
    audios = poem.audios.filter(is_uploaded=True)

    context = {
        "poem": poem,
        "verses_map": verses_map,
        "single_verses": single_verses,
        "breadcrumbs": breadcrumbs,
        "audios": audios,
    }

    return render(request, "core/poem_detail.html", context)


@login_required
def favorites(request):
    """
    Display user's favorite poems and verses.

    Args:
        request: HTTP request object

    Returns:
        Rendered favorites page
    """
    favs = request.user.ganjoor_favorites.select_related(
        "poem__category__poet", "verse"
    ).order_by("-created_at")

    return render(request, "core/favorites.html", {"favorites": favs})


def search(request):
    """
    Search for poems by title or verse content.

    Args:
        request: HTTP request object with 'q' parameter

    Returns:
        Rendered search results page
    """
    query = request.GET.get("q", "").strip()
    poet_id = request.GET.get("poet")

    poems = GanjoorPoem.objects.none()

    if query:
        # Use select_related to avoid N+1 queries
        poems_qs = GanjoorPoem.objects.select_related("category__poet")

        # Filter by poet if specified
        if poet_id:
            try:
                poems_qs = poems_qs.filter(category__poet_id=int(poet_id))
            except (ValueError, TypeError):
                pass

        # Search in title and verse text
        poems = poems_qs.filter(
            Q(title__icontains=query) | Q(verses__text__icontains=query)
        ).distinct()[:100]  # Limit results

    # Get all poets for filter dropdown
    poets = GanjoorPoet.objects.all().order_by("name")

    context = {
        "poems": poems,
        "query": query,
        "poets": poets,
        "selected_poet_id": int(poet_id) if poet_id else None,
    }

    return render(request, "core/search_results.html", context)


# -------------------
# DRF ViewSets
# -------------------
class GanjoorPoetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing poets.

    Provides CRUD operations for poets with filtering and search.
    """

    queryset = GanjoorPoet.objects.all().order_by("name")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["name", "description"]
    filterset_fields = ["century"]
    ordering_fields = ["name", "century", "id"]
    ordering = ["name"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return GanjoorPoetListSerializer
        return GanjoorPoetSerializer

    @action(detail=True, methods=["get"])
    def categories(self, request, pk=None):
        """Get all categories for a specific poet."""
        poet = self.get_object()
        categories = poet.categories.filter(parent=None).order_by("title")
        serializer = GanjoorCategoryListSerializer(
            categories, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def poems(self, request, pk=None):
        """Get all poems for a specific poet."""
        poet = self.get_object()
        poems = (
            GanjoorPoem.objects.select_related("category__poet")
            .filter(category__poet=poet)
            .order_by("title")
        )

        # Apply pagination
        page = self.paginate_queryset(poems)
        if page is not None:
            serializer = GanjoorPoemListSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = GanjoorPoemListSerializer(
            poems, many=True, context={"request": request}
        )
        return Response(serializer.data)


class GanjoorCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing categories.

    Provides CRUD operations for categories with filtering and search.
    """

    queryset = GanjoorCategory.objects.all().select_related("poet", "parent")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["title"]
    filterset_fields = ["poet", "parent"]
    ordering_fields = ["title", "id"]
    ordering = ["title"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return GanjoorCategoryListSerializer
        return GanjoorCategorySerializer

    @action(detail=True, methods=["get"])
    def poems(self, request, pk=None):
        """Get all poems in a specific category."""
        category = self.get_object()
        poems = category.poems.select_related("category__poet").order_by("title")

        # Apply pagination
        page = self.paginate_queryset(poems)
        if page is not None:
            serializer = GanjoorPoemListSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = GanjoorPoemListSerializer(
            poems, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def subcategories(self, request, pk=None):
        """Get all subcategories of a specific category."""
        category = self.get_object()
        subcategories = category.children.all().order_by("title")
        serializer = GanjoorCategoryListSerializer(
            subcategories, many=True, context={"request": request}
        )
        return Response(serializer.data)


class GanjoorPoemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing poems.

    Provides CRUD operations for poems with filtering and search.
    """

    queryset = GanjoorPoem.objects.all().select_related("category__poet")
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["title", "verses__text"]
    filterset_fields = ["category", "category__poet"]
    ordering_fields = ["title", "id"]
    ordering = ["title"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return GanjoorPoemListSerializer
        return GanjoorPoemSerializer

    def get_queryset(self):
        """Optimize queryset with prefetch_related for verses."""
        queryset = super().get_queryset()
        if self.action == "retrieve":
            queryset = queryset.prefetch_related("verses", "audios")
        return queryset

    @action(detail=True, methods=["get"])
    def verses(self, request, pk=None):
        """Get all verses for a specific poem."""
        poem = self.get_object()
        verses = poem.verses.all().order_by("order", "position")
        serializer = GanjoorVerseSerializer(
            verses, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def search(self, request):
        """
        Search poems by title or verse content.

        Query params:
            - q: search query
            - poet: filter by poet ID
        """
        query = request.query_params.get("q", "").strip()
        poet_id = request.query_params.get("poet")

        if not query:
            return Response(
                {
                    "error": "validation_error",
                    "message": str(_("Please provide a search query.")),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset()

        # Filter by poet if specified
        if poet_id:
            queryset = queryset.filter(category__poet_id=poet_id)

        # Search in title and verses
        queryset = queryset.filter(
            Q(title__icontains=query) | Q(verses__text__icontains=query)
        ).distinct()

        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class GanjoorVerseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing verses.

    Provides CRUD operations for verses with filtering.
    """

    queryset = GanjoorVerse.objects.all().select_related("poem")
    serializer_class = GanjoorVerseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["text"]
    filterset_fields = ["poem", "position"]
    ordering_fields = ["order", "id"]
    ordering = ["order"]


class GanjoorFavoriteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user favorites.

    Users can only view and manage their own favorites.
    """

    serializer_class = GanjoorFavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["poem", "verse"]
    ordering_fields = ["created_at", "id"]
    ordering = ["-created_at"]

    def get_queryset(self):
        """Return only the current user's favorites."""
        return GanjoorFavorite.objects.filter(user=self.request.user).select_related(
            "poem__category__poet", "verse"
        )

    def perform_create(self, serializer):
        """Automatically set the user when creating a favorite."""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"])
    def toggle(self, request):
        """
        Toggle a favorite (add if doesn't exist, remove if exists).

        Request body:
            - poem: poem ID
            - verse: verse ID
        """
        poem_id = request.data.get("poem")
        verse_id = request.data.get("verse")

        if not poem_id or not verse_id:
            return Response(
                {
                    "error": "validation_error",
                    "message": str(_("Poem and verse IDs are required.")),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            favorite = GanjoorFavorite.objects.get(
                user=request.user, poem_id=poem_id, verse_id=verse_id
            )
            favorite.delete()
            return Response(
                {
                    "status": "removed",
                    "message": str(_("Removed from favorites.")),
                },
                status=status.HTTP_200_OK,
            )
        except GanjoorFavorite.DoesNotExist:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                {
                    "status": "added",
                    "message": str(_("Added to favorites.")),
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )


class GanjoorPoemAudioViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing poem audio files.

    Provides CRUD operations for audio files with filtering.
    """

    queryset = GanjoorPoemAudio.objects.all().select_related("poem")
    serializer_class = GanjoorPoemAudioSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["poem", "is_uploaded", "is_direct"]
    ordering_fields = ["id"]
    ordering = ["id"]


class GanjoorAudioSyncViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing audio synchronization data.

    Provides CRUD operations for audio sync points.
    """

    queryset = GanjoorAudioSync.objects.all().select_related("poem", "audio")
    serializer_class = GanjoorAudioSyncSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["poem", "audio"]
    ordering_fields = ["verse_order", "millisec"]
    ordering = ["verse_order"]


class UserSettingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user settings.

    Users can only view and manage their own settings.
    """

    serializer_class = UserSettingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return only the current user's settings."""
        return UserSetting.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Automatically set the user when creating settings."""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get", "post"])
    def me(self, request):
        """
        Get or update current user's settings.

        GET: Returns current user's settings
        POST: Updates current user's settings
        """
        try:
            settings = UserSetting.objects.get(user=request.user)
        except UserSetting.DoesNotExist:
            if request.method == "GET":
                return Response(
                    {
                        "error": "not_found",
                        "message": str(_("Settings not found for this user.")),
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
            # Create new settings
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "POST":
            serializer = self.get_serializer(settings, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        serializer = self.get_serializer(settings)
        return Response(serializer.data)
