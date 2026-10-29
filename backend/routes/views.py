from django.contrib.gis.db.models import GeometryField
from django.contrib.gis.db.models.functions import Intersection, Length, Transform
from django.contrib.gis.measure import D
from django.db.models import Sum, Value
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import AvoidanceArea, LightingAsset, StreetSegment, StudyArea
from .permissions import StaffWriteOrReadOnly
from .serializers import (
    AvoidanceAreaSerializer,
    LightingAssetSerializer,
    RouteEvidenceSerializer,
    StreetSegmentSerializer,
    StudyAreaSerializer,
)


class StaffManagedSpatialViewSet(viewsets.ModelViewSet):
    permission_classes = (StaffWriteOrReadOnly,)


class StudyAreaViewSet(StaffManagedSpatialViewSet):
    queryset = StudyArea.objects.all()
    serializer_class = StudyAreaSerializer


class LightingAssetViewSet(StaffManagedSpatialViewSet):
    queryset = LightingAsset.objects.all()
    serializer_class = LightingAssetSerializer


class StreetSegmentViewSet(StaffManagedSpatialViewSet):
    queryset = StreetSegment.objects.all()
    serializer_class = StreetSegmentSerializer


class AvoidanceAreaViewSet(StaffManagedSpatialViewSet):
    queryset = AvoidanceArea.objects.all()
    serializer_class = AvoidanceAreaSerializer


@api_view(["POST"])
def route_evidence(request):
    serializer = RouteEvidenceSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    route = serializer.validated_data["route"]
    buffer_m = serializer.validated_data["buffer_m"]

    route_metric = route.clone()
    route_metric.transform(2157)

    nearby_lights = (
        LightingAsset.objects.annotate(location_metric=Transform("location", 2157))
        .filter(location_metric__dwithin=(route_metric, D(m=buffer_m)))
        .count()
    )

    avoidance_intersections = list(
        AvoidanceArea.objects.filter(boundary__intersects=route)
        .values("id", "name", "category")
        .order_by("name", "id")
    )

    segments = (
        StreetSegment.objects.annotate(geometry_metric=Transform("geometry", 2157))
        .filter(geometry_metric__intersects=route_metric)
        .annotate(
            overlap=Intersection(
                "geometry_metric",
                Value(route_metric, output_field=GeometryField(srid=2157)),
            ),
            overlap_length=Length("overlap"),
        )
    )
    lit_length = segments.filter(lit_value__in=["yes", "automatic"]).aggregate(
        total=Sum("overlap_length")
    )["total"]
    unlit_length = segments.filter(lit_value="no").aggregate(total=Sum("overlap_length"))["total"]

    lit_m = lit_length.m if lit_length else 0.0
    unlit_m = unlit_length.m if unlit_length else 0.0
    route_length_m = route_metric.length
    unknown_m = max(route_length_m - lit_m - unlit_m, 0.0)

    return Response(
        {
            "buffer_m": buffer_m,
            "lighting_assets_within_buffer": nearby_lights,
            "avoidance_intersections": avoidance_intersections,
            "route_length_m": round(route_length_m, 1),
            "mapped_lighting_tag_length_m": {
                "tagged_lit_m": round(lit_m, 1),
                "tagged_unlit_m": round(unlit_m, 1),
                "unknown_or_unmapped_m": round(unknown_m, 1),
            },
            "interpretation": (
                "Mapped lighting tags and asset locations are incomplete and do not confirm "
                "that a light is working or that a route is safe."
            ),
        },
        status=status.HTTP_200_OK,
    )
from django.shortcuts import render


def map_home(request):
    return render(request, "map.html")
