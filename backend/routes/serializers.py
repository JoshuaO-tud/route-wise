import json

from django.contrib.gis.geos import GEOSException, GEOSGeometry
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import AvoidanceArea, LightingAsset, StreetSegment, StudyArea


class StudyAreaSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = StudyArea
        geo_field = "boundary"
        fields = ("id", "name", "description")


class LightingAssetSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = LightingAsset
        geo_field = "location"
        fields = ("id", "source_id", "asset_type", "source_updated", "source_attributes")


class StreetSegmentSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = StreetSegment
        geo_field = "geometry"
        fields = (
            "id",
            "source_id",
            "name",
            "highway",
            "lit_value",
            "sidewalk_value",
            "source_attributes",
        )


class AvoidanceAreaSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = AvoidanceArea
        geo_field = "boundary"
        fields = ("id", "name", "category", "created_at", "updated_at")
        read_only_fields = ("created_at", "updated_at")


class RouteEvidenceSerializer(serializers.Serializer):
    route = serializers.JSONField()
    buffer_m = serializers.FloatField(min_value=5, max_value=100, default=20)

    def validate_route(self, value):
        if value.get("type") == "Feature":
            value = value.get("geometry")
        if not isinstance(value, dict):
            raise serializers.ValidationError("Provide a GeoJSON LineString geometry.")
        try:
            geometry = GEOSGeometry(json.dumps(value), srid=4326)
        except (GEOSException, TypeError, ValueError) as exc:
            raise serializers.ValidationError("The route geometry is not valid GeoJSON.") from exc
        if geometry.geom_type != "LineString":
            raise serializers.ValidationError("The route must be a LineString.")
        if not geometry.valid or geometry.empty:
            raise serializers.ValidationError("The route must be non-empty and valid.")
        return geometry

