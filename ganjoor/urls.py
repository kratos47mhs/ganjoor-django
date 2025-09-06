from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.api_urls")),      # API endpoints: /api/poets/, /api/poems/, etc.
    path("mcp/", include('mcp_server.urls')),    # Extra app, if used
    path('', include('core.urls', namespace='core')),  # Web frontend
]