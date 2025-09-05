from rest_framework.routers import DefaultRouter
from .views import (
    GanjoorPoetViewSet,
    GanjoorPoemViewSet,
    GanjoorFavoriteViewSet,
    GanjoorPoemAudioViewSet,
    UserSettingViewSet,
)

router = DefaultRouter()
router.register(r"poets", GanjoorPoetViewSet, basename="poet")
router.register(r"poems", GanjoorPoemViewSet, basename="poem")
router.register(r"favorites", GanjoorFavoriteViewSet, basename="favorite")
router.register(r"audio", GanjoorPoemAudioViewSet, basename="audio")
router.register(r"user/settings", UserSettingViewSet, basename="user-settings")

urlpatterns = router.urls
