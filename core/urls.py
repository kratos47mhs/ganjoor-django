from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = "core"  # <--- This is important!

urlpatterns = [
    path("", views.home, name="home"),
    path("poet/<int:pk>/", views.poet_detail, name="poet_detail"),
    path("category/<int:pk>/", views.category_detail, name="category_detail"),
    path("poem/<int:pk>/", views.poem_detail, name="poem_detail"),
    path("favorites/", views.favorites, name="favorites"),
    path("search/", views.search, name="search"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
