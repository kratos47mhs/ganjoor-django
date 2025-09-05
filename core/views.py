from rest_framework import viewsets
from .models import GanjoorPoet, GanjoorCat, GanjoorPoem, GanjoorVerse
from .serializers import (
    GanjoorPoetSerializer,
    GanjoorCatSerializer,
    GanjoorPoemSerializer,
    GanjoorVerseSerializer,
)


class GanjoorPoetViewSet(viewsets.ModelViewSet):
    queryset = GanjoorPoet.objects.all()
    serializer_class = GanjoorPoetSerializer


class GanjoorCatViewSet(viewsets.ModelViewSet):
    queryset = GanjoorCat.objects.all()
    serializer_class = GanjoorCatSerializer


class GanjoorPoemViewSet(viewsets.ModelViewSet):
    queryset = GanjoorPoem.objects.all()
    serializer_class = GanjoorPoemSerializer


class GanjoorVerseViewSet(viewsets.ModelViewSet):
    queryset = GanjoorVerse.objects.all()
    serializer_class = GanjoorVerseSerializer
