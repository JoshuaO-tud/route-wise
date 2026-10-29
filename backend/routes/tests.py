from django.contrib.auth import get_user_model
from django.contrib.gis.geos import LineString, Point, Polygon
from django.test import TestCase
from rest_framework.test import APIClient

from .models import AvoidanceArea, LightingAsset, StreetSegment


class SpatialLayerApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.route_coordinates = [
            [-6.2600, 53.3450],
            [-6.2550, 53.3450],
        ]
        self.route_payload = {
            "route": {
                "type": "LineString",
                "coordinates": self.route_coordinates,
            },
            "buffer_m": 20,
        }

    def test_public_user_can_list_lighting_assets(self):
        LightingAsset.objects.create(
            source_id="dcc-1001",
            asset_type="street_light",
            location=Point(-6.257, 53.345, srid=4326),
        )

        response = self.client.get("/api/lighting-assets/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["features"]), 1)

    def test_anonymous_user_cannot_create_lighting_asset(self):
        response = self.client.post(
            "/api/lighting-assets/",
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [-6.257, 53.345],
                },
                "properties": {
                    "source_id": "dcc-1002",
                    "asset_type": "street_light",
                    "source_attributes": {},
                },
            },
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(LightingAsset.objects.count(), 0)

    def test_staff_user_can_create_lighting_asset(self):
        user = get_user_model().objects.create_user(
            username="staff-user",
            password="test-password",
            is_staff=True,
        )
        self.client.force_authenticate(user=user)

        response = self.client.post(
            "/api/lighting-assets/",
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [-6.257, 53.345],
                },
                "properties": {
                    "source_id": "dcc-1003",
                    "asset_type": "street_light",
                    "source_attributes": {},
                },
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(LightingAsset.objects.get().source_id, "dcc-1003")

    def test_invalid_route_geometry_is_rejected(self):
        response = self.client.post(
            "/api/spatial/route-evidence/",
            {"route": {"type": "Point", "coordinates": [-6.26, 53.345]}},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_route_evidence_runs_the_three_spatial_queries(self):
        route = LineString(*self.route_coordinates, srid=4326)
        LightingAsset.objects.create(
            source_id="near-route",
            asset_type="street_light",
            location=Point(-6.2575, 53.3451, srid=4326),
        )
        StreetSegment.objects.create(
            source_id="osm-way-1",
            highway="footway",
            lit_value="yes",
            geometry=route,
        )
        AvoidanceArea.objects.create(
            name="Temporary avoidance",
            boundary=Polygon(
                (
                    (-6.258, 53.344),
                    (-6.257, 53.344),
                    (-6.257, 53.346),
                    (-6.258, 53.346),
                    (-6.258, 53.344),
                ),
                srid=4326,
            ),
        )

        response = self.client.post(
            "/api/spatial/route-evidence/",
            self.route_payload,
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["lighting_assets_within_buffer"], 1)
        self.assertEqual(len(response.data["avoidance_intersections"]), 1)
        self.assertGreater(
            response.data["mapped_lighting_tag_length_m"]["tagged_lit_m"],
            0,
        )
