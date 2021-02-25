import click
import os
import json
import logging

from osmox import config, build


default_config_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../configs/config.json")
)
default_input_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../tests/data/isle-of-man-latest.osm.pbf")
)
default_output_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../outputs/example.geojson")
)
logger = logging.getLogger(__name__)

@click.group()
def osmox():
    """
    Access cli.
    """
    pass


@osmox.command()    
@click.argument("config_path", nargs=1, type=click.Path(exists=True), required=True)
def validate(config_path):
    """
    Validate a config.
    """
    cnfg = config.load(config_path)
    config.validate_activity_config(cnfg)
    logger.warning(f"Done.")


@osmox.command()
@click.option("-c", "--config_path", type=click.Path(exists=True), default=default_config_path,
              help="Path to config, eg './configs/default.csv'")
@click.option("-i", "--input_path", type=click.Path(exists=False), default=default_input_path,
              help="Path to input osm map, eg './example.osm.pbf'")
@click.option("-o", "--output_path", type=click.Path(exists=False), default=default_output_path,
              help="Putput path, eg './example.geojson'")
def run(config_path, input_path, output_path):

    logger.info(f" Loading config from {config_path}")
    cnfg = config.load(config_path)
    config.validate_activity_config(cnfg)
    handler = build.ObjectHandler(cnfg)
    handler.apply_file(input_path, locations=True, idx='flex_mem')
    logger.info(f" Found {len(handler.objects)} buildings.")
    logger.info(f" Found {len(handler.points)} nodes with valid tags.")
    logger.info(f" Found {len(handler.areas)} areas with valid tags.")

    logger.info(f" Assigning building tags.")
    handler.assign_tags()
    logger.info(f" Finished assigning tags: f{handler.log}.")

    logger.info(f" Assigning building activities.")
    handler.assign_activities()

    if 'transit_stop' in config.get_acts(cnfg):
        logger.info(f" Assigning distances from nearest transit stop.")
        handler.assign_transit_stop_distances()

    if cnfg.get("features_config"):
        logger.info(f" Assigning building features: {cnfg['features_config']}.")
        handler.add_features()

    gdf = handler.dataframe()

    logger.info(f" Outputting facility sample {output_path}")
    with open(output_path, "w") as file:
        file.write(gdf.to_json())
    logger.info("Done.")
