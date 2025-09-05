# core/serializers.py
from rest_framework import serializers
from .models import GanjoorPoet, GanjoorCat, GanjoorPoem, GanjoorVerse


class GanjoorPoetSerializer(serializers.ModelSerializer):
    class Meta:
        model = GanjoorPoet
        fields = "__all__"


class GanjoorCatSerializer(serializers.ModelSerializer):
    class Meta:
        model = GanjoorCat
        fields = "__all__"


class GanjoorPoemSerializer(serializers.ModelSerializer):
    class Meta:
        model = GanjoorPoem
        fields = "__all__"


class GanjoorVerseSerializer(serializers.ModelSerializer):
    class Meta:
        model = GanjoorVerse
        fields = "__all__"
