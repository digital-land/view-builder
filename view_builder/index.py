import sqlite3
import sys

is_mac_os = sys.platform == "darwin"

lib = (
    "/usr/local/lib/mod_spatialite.dylib"
    if is_mac_os
    else "/usr/lib/x86_64-linux-gnu/mod_spatialite.so"
)


def index_view_model(path):
    conn = sqlite3.connect(path)

    # Lead the spatialite extension:
    conn.enable_load_extension(True)
    conn.load_extension(lib)

    # Initialize spatial metadata for this database:
    conn.execute("SELECT InitSpatialMetadata(1)")

    # Add a geometry column called point_geom to our museums table:
    conn.execute(
        "SELECT AddGeometryColumn('geography', 'geom', 4326, 'MULTIPOLYGON', 2);"
    )

    # TODO: Lets think more about the layout of our view model. We should probably
    #       keep the geography table untouched and create views that have the geoJSON
    #       pre-baked for various zoom levels.

    # Now update that geometry column with the lat/lon points
    conn.execute(
        """
        UPDATE geography SET
        geom = GeomFromText(geometry,4326);
    """
    )

    # Now copy the data back to geometry as geoJSON
    conn.execute(
        """
        UPDATE geography SET
        geometry= AsGeoJSON(geom)
    """
    )

    # Now add a spatial index to that column
    conn.execute('SELECT CreateSpatialIndex("geography", "geom");')

    # Finally drop the automatically created KNN table as it's not compatible
    # with datasette package as yet
    conn.execute("DROP TABLE IF EXISTS KNN")

    # Build our row into a full geoJSON feature for quick map fetches
    conn.execute("""DROP VIEW IF EXISTS v_geography_simplified""")
    conn.execute("""
        CREATE VIEW v_geography_simplified
        AS
        SELECT
            g.rowid AS rowid,
            json_object('type', 'Feature', 'id', g.rowid, 'properties', json_object('name', name, 'type', g.type, 'slug', s.slug, 'rowid', g.rowid, 'entry-date', entry_date, 'start-date', start_date, 'end-date', end_date), 'geometry', AsGeoJSON(Simplify(g.geom, 0.0005))) AS simple_features,
            json_object('type', 'Feature', 'id', g.rowid, 'properties', json_object('name', name, 'type', g.type, 'slug', s.slug, 'rowid', g.rowid, 'entry-date', entry_date, 'start-date', start_date, 'end-date', end_date), "geometry", AsGeoJSON(geom)) AS features
        FROM
            geography AS g
        JOIN slug AS s ON g.slug_id = s.id
    """)

    # If you don't commit your changes will not be persisted:
    conn.commit()
    conn.close()
