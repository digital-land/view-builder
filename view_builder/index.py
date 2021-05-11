import sqlite3


def index_view_model(path):
    conn = sqlite3.connect(path)

    # Lead the spatialite extension:
    conn.enable_load_extension(True)
    conn.load_extension("/usr/local/lib/mod_spatialite.dylib")

    # Initialize spatial metadata for this database:
    conn.execute("select InitSpatialMetadata(1)")

    # Add a geometry column called point_geom to our museums table:
    conn.execute(
        "SELECT AddGeometryColumn('geography', 'geom', 4326, 'MULTIPOLYGON', 2);"
    )

    # Now update that geometry column with the lat/lon points
    conn.execute(
        """
        UPDATE geography SET
        geom = GeomFromText(geometry,4326);
    """
    )

    # Now add a spatial index to that column
    conn.execute('select CreateSpatialIndex("geography", "geom");')

    # If you don't commit your changes will not be persisted:
    conn.commit()
    conn.close()
