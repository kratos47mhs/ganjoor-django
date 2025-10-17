from rest_framework import serializers
from .models import *

class GanjoorPoetSerializer(serializers.ModelSerializer):
    class Meta:
        model = GanjoorPoet
        fields = "__all__"

class GanjoorCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GanjoorCategory
        fields = "__all__"

class GanjoorPoemSerializer(serializers.ModelSerializer):
    class Meta:
        model = GanjoorPoem
        fields = "__all__"

class GanjoorVerseSerializer(serializers.ModelSerializer):
    class Meta:
        model = GanjoorVerse
        fields = "__all__"

class GanjoorFavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = GanjoorFavorite
        fields = "__all__"

class GanjoorPoemAudioSerializer(serializers.ModelSerializer):
    class Meta:
        model = GanjoorPoemAudio
        fields = "__all__"

class GanjoorAudioSyncSerializer(serializers.ModelSerializer):
    class Meta:
        model = GanjoorAudioSync
        fields = "__all__"

class UserSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSetting
        fields = "__all__"