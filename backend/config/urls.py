from django.contrib import admin
from django.urls import include, path

from routes.views import map_home

urlpatterns = [
    path("", map_home, name="map-home"),
    path("admin/", admin.site.urls),
    path("api/", include("routes.urls")),
]
