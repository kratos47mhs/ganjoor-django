"""
URL configuration for ganjoor project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from core.views import (
    GanjoorPoetViewSet,
    GanjoorCatViewSet,
    GanjoorPoemViewSet,
    GanjoorVerseViewSet,
    GanjoorFavoriteViewSet,
)

router = routers.DefaultRouter()
router.register(r"poets", GanjoorPoetViewSet)
router.register(r"categories", GanjoorCatViewSet)
router.register(r"poems", GanjoorPoemViewSet)
router.register(r"verses", GanjoorVerseViewSet)
router.register(r"favorites", GanjoorFavoriteViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
