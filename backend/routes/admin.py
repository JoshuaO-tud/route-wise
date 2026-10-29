from django.contrib import admin

from .models import AvoidanceArea, LightingAsset, StreetSegment, StudyArea


@admin.register(StudyArea)
class StudyAreaAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(LightingAsset)
class LightingAssetAdmin(admin.ModelAdmin):
    list_display = ("source_id", "asset_type", "source_updated")
    search_fields = ("source_id", "asset_type")


@admin.register(StreetSegment)
class StreetSegmentAdmin(admin.ModelAdmin):
    list_display = ("source_id", "name", "highway", "lit_value", "sidewalk_value")
    search_fields = ("source_id", "name", "highway")
    list_filter = ("highway", "lit_value", "sidewalk_value")


@admin.register(AvoidanceArea)
class AvoidanceAreaAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "created_at")
    search_fields = ("name",)
    list_filter = ("category",)
