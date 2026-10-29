from django.contrib.gis.db import models


class StudyArea(models.Model):
    name = models.CharField(max_length=120, unique=True)
    boundary = models.PolygonField(srid=4326, spatial_index=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class LightingAsset(models.Model):
    source_id = models.CharField(max_length=80, unique=True)
    asset_type = models.CharField(max_length=80, blank=True)
    location = models.PointField(srid=4326, spatial_index=True)
    source_updated = models.DateField(null=True, blank=True)
    source_attributes = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["source_id"]

    def __str__(self):
        return f"{self.source_id} ({self.asset_type or 'type unknown'})"


class StreetSegment(models.Model):
    source_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200, blank=True)
    highway = models.CharField(max_length=60)
    lit_value = models.CharField(max_length=30, blank=True, null=True)
    sidewalk_value = models.CharField(max_length=60, blank=True, null=True)
    geometry = models.LineStringField(srid=4326, spatial_index=True)
    source_attributes = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["name", "source_id"]

    def __str__(self):
        return self.name or f"{self.highway} {self.source_id}"


class AvoidanceArea(models.Model):
    name = models.CharField(max_length=120)
    category = models.CharField(max_length=60, blank=True)
    boundary = models.PolygonField(srid=4326, spatial_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "id"]

    def __str__(self):
        return self.name
