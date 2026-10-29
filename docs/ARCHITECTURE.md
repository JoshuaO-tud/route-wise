# RouteWise Dublin architecture

The browser map calls the same-origin Django API. Django uses PostGIS to store and query spatial layers and communicates with the private Valhalla service for routing. Leaflet renders the map, API features and route geometry.

~~~mermaid
flowchart LR
    Browser[Leaflet browser UI] -->|same-origin HTTP| Django[Django + REST API]
    Django -->|SQL / PostGIS| DB[(PostgreSQL + PostGIS)]
    Django -->|route requests| Valhalla[Valhalla routing engine]
    PgAdmin[PgAdmin4] --> DB
~~~

Compose runs these services on an isolated bridge network with a declared custom subnet. PostgreSQL and PgAdmin state persist in named volumes. The OSM PBF and generated Valhalla graph stay under the ignored local data directory and are not committed.

The map displays GeoJSON from the lighting asset, street segment and avoidance area API endpoints. Users can toggle those layers and inspect feature properties. The route-evidence API accepts a proposed line and reports nearby lighting assets, mapped avoidance-area overlaps, and the length of intersecting street segments with recorded lighting tags. These records have incomplete coverage and do not measure personal safety or confirm that a light is operational.

Route previews are stateless by default. Public source layers are read-only to ordinary visitors. Staff users can manage spatial source and reference records through the API and Django admin.
