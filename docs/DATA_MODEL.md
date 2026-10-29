# Initial spatial data model

All geometry is stored in WGS84 (SRID 4326) and each GeoDjango geometry field creates a PostGIS spatial index.

| Model | Geometry | Purpose | API write access |
|---|---|---|---|
| StudyArea | Polygon | Demonstration boundary used to constrain and explain coverage. | Staff only |
| LightingAsset | Point | DCC mapped lighting asset. Its operational state is unknown. | Staff only |
| StreetSegment | LineString | Imported OSM road/pedestrian segment and selected raw tags. Missing tags remain null/unknown. | Staff only |
| AvoidanceArea | Polygon | Named avoidance layer. User route requests may submit transient polygons; saving shared areas is an explicit staff action. | Staff only |

The initial design avoids storing personal route history. Reference data CRUD is available to authenticated staff; read access is public.

## PostGIS query endpoint

1. ST_DWithin: count or return lighting assets near a route corridor, with distance in meters and a warning that historical assets do not prove current lighting.
2. ST_Intersects: test a candidate route against submitted or saved avoidance polygons and reject/flag intersections.
3. ST_Intersection and length: intersect a route with mapped street segments to report what proportion of distance overlaps segments with a known lit tag; report unknown-tag length separately.

All three queries are implemented in POST /api/spatial/route-evidence/. Automated tests cover nearby assets, avoidance intersections, route-tag coverage, and invalid geometry. The tests still need to run against the CA1 PostGIS service. The results are contextual indicators, not a safety score.

