# RouteWise Dublin

RouteWise is a small web mapping project for exploring route choices in Dublin alongside the public information available for each area. Its aim is to make route context easier to inspect, including where the underlying map data is incomplete. It does not provide a safety rating or guarantee that a route is safe.

## Current build

The project has an independent Django and PostGIS backend, GeoJSON API layers for study areas, lighting assets, street segments and avoidance areas, and a responsive Leaflet map at the site root. The map can show or hide the API layers and open feature details. Route evidence analysis is available through `POST /api/spatial/route-evidence/` for a supplied line geometry.

The API and browser interface are implemented, but the full application has not yet been run end to end in this environment. Database migrations, loading the Dublin source data, local Valhalla graph startup, and browser verification remain to be completed.

## Stack

- Django 5.2 and Django REST Framework
- PostgreSQL with PostGIS
- Leaflet for the interactive map
- Docker Compose for Django, PostGIS, PgAdmin4 and Valhalla

## Local setup

1. Copy `.env.example` to `.env` and set local development values. Keep `.env` private.
2. Place the Dublin OpenStreetMap PBF in `data/valhalla/`. The PBF and generated routing graph are excluded from Git.
3. Start the services with `docker compose -p routewise up --build -d`.
4. Run Django migrations in the web container and check the service health.
5. Open the map at <http://localhost:8010>, PgAdmin at <http://localhost:5052>, and the local Valhalla service at <http://localhost:8012>.

The first startup can take time while Valhalla builds its routing graph from the local PBF. Database and PgAdmin state use named Docker volumes.

## Data and interpretation

The pilot area is central Dublin. Public lighting records describe recorded assets; they do not establish whether a light is currently working. OpenStreetMap tags and other public records can be missing or out of date. The interface should present unknown coverage as unknown and make the source and limits of each data layer clear. Route comparisons are contextual information, not safety advice.

The map uses the FOSSGIS tile service operated through OpenStreetMap Deutschland, with visible OpenStreetMap and FOSSGIS attribution. Feature data comes from this project's own API.

## Documentation

See `docs/ARCHITECTURE.md` for the service layout and `docs/DATA_MODEL.md` for the spatial layers and query design. Source dataset provenance and limitations are recorded in the local data audit notes.

