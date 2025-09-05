from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    GanjoorPoet,
    GanjoorPoem,
    GanjoorFavorite,
    GanjoorPoemAudio,
    UserSetting,
    GanjoorVerse,
    GanjoorCat,
)
from .serializers import (
    GanjoorPoetSerializer,
    GanjoorPoemSerializer,
    GanjoorCatSerializer,
    GanjoorFavoriteSerializer,
    GanjoorVerseSerializer,
    GanjoorPoemAudioSerializer,
    UserSettingSerializer,
)
from django.shortcuts import get_object_or_404
import random


class GanjoorCatViewSet(viewsets.ModelViewSet):
    queryset = GanjoorCat.objects.all()
    serializer_class = GanjoorCatSerializer


class GanjoorVerseViewSet(viewsets.ModelViewSet):
    queryset = GanjoorVerse.objects.all()
    serializer_class = GanjoorVerseSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["text"]


# -------------------
# Poet ViewSet
# -------------------
class GanjoorPoetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GanjoorPoet.objects.all()
    serializer_class = GanjoorPoetSerializer


# -------------------
# Poem ViewSet
# -------------------
class GanjoorPoemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GanjoorPoem.objects.all()
    serializer_class = GanjoorPoemSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["category", "category__poet"]
    search_fields = ["title", "slug"]

    @action(detail=False, methods=["get"])
    def random(self, request):
        poems = list(GanjoorPoem.objects.all())
        if poems:
            poem = random.choice(poems)
            serializer = self.get_serializer(poem)
            return Response(serializer.data)
        return Response(
            {"detail": "No poems available."}, status=status.HTTP_404_NOT_FOUND
        )


# -------------------
# Favorite ViewSet
# -------------------
class GanjoorFavoriteViewSet(viewsets.ModelViewSet):
    queryset = GanjoorFavorite.objects.all()
    serializer_class = GanjoorFavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GanjoorFavorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# -------------------
# PoemAudio ViewSet
# -------------------
class GanjoorPoemAudioViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GanjoorPoemAudioSerializer
    queryset = GanjoorPoemAudio.objects.all()

    @action(detail=True, methods=["get"])
    def stream(self, request, pk=None):
        poem_audio = get_object_or_404(GanjoorPoemAudio, pk=pk)
        file_handle = poem_audio.file.open("rb")
        response = Response(file_handle.read(), content_type="audio/mpeg")
        response["Content-Disposition"] = f'inline; filename="{poem_audio.file.name}"'
        return response


# -------------------
# User Setting ViewSet
# -------------------
class UserSettingViewSet(viewsets.ModelViewSet):
    serializer_class = UserSettingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        setting, created = UserSetting.objects.get_or_create(user=self.request.user)
        return setting
