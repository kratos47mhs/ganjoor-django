from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import GanjoorPoetViewSet, GanjoorCategoryViewSet, GanjoorPoemViewSet, GanjoorVerseViewSet, GanjoorFavoriteViewSet, GanjoorPoemAudioViewSet, GanjoorAudioSyncViewSet, UserSettingViewSet

router = DefaultRouter()
router.register(r"poets", GanjoorPoetViewSet)
router.register(r"categories", GanjoorCategoryViewSet)
router.register(r"poems", GanjoorPoemViewSet)
router.register(r"verses", GanjoorVerseViewSet)
router.register(r"audios", GanjoorPoemAudioViewSet)
router.register(r"audio-syncs", GanjoorAudioSyncViewSet)
router.register(r"settings", UserSettingViewSet, basename="setting")
router.register(r"favorites", GanjoorFavoriteViewSet, basename="favorite")

urlpatterns = [
    path("", include(router.urls)),
]
