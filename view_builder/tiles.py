import sqlite3
from datasette_builder.build import run


def build_tiles_for_datasets(view_model_path, output_path):
    datasets = get_geography_datasets(view_model_path)
    for dataset in datasets:
        dump_geometry_to_file(dataset[0], view_model_path, output_path)
        convert_geometry_to_geojson(dataset[0], output_path)
        build_tiles(dataset[0], output_path)


def get_geography_datasets(view_model_path):
    conn = sqlite3.connect(view_model_path)
    cur = conn.cursor()
    cur.execute("select DISTINCT type from geography_geom")
    geography_datasets = list(cur.fetchall())
    conn.close()
    return geography_datasets


def dump_geometry_to_file(dataset, view_model_path, output_path):
    dump_geom_cmd = [
        "sqlite3",
        view_model_path,
        f".output {output_path}{dataset}.txt",
        f"SELECT json_patch(geojson_full, json_object('tippecanoe', json_object('layer', type))) from geography_geom WHERE type='{dataset}'",
    ]
    run(dump_geom_cmd)


def convert_geometry_to_geojson(dataset, output_path):
    with open(output_path + f"{dataset}.txt", "r") as f:
        geometry_text = f.read()
        geojson = (
            '{"type":"FeatureCollection","features":['
            + geometry_text.replace("\n", ",")[:-1]
            + "]}"
        )

    with open(output_path + f"{dataset}.geojson", "w") as f:
        f.write(geojson)


def build_tiles(dataset, output_path):
    build_tiles_cmd = [
        "tippecanoe",
        "-z15",
        "-Z4",
        "-r1",
        "--no-feature-limit",
        "--no-tile-size-limit",
        f"--layer={dataset}",
        f"--output={output_path}{dataset}.mbtiles",
        f"{output_path}{dataset}.geojson",
    ]
    run(build_tiles_cmd)
