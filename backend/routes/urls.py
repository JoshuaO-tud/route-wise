from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AvoidanceAreaViewSet,
    LightingAssetViewSet,
    StreetSegmentViewSet,
    StudyAreaViewSet,
    route_evidence,
)

router = DefaultRouter()
router.register("study-areas", StudyAreaViewSet)
router.register("lighting-assets", LightingAssetViewSet)
router.register("street-segments", StreetSegmentViewSet)
router.register("avoidance-areas", AvoidanceAreaViewSet)

urlpatterns = [
    path("spatial/route-evidence/", route_evidence, name="route-evidence"),
    *router.urls,
]
