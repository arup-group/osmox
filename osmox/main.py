import logging
import os

import click

from osmox import config, build
from osmox.helpers import PathPath
from osmox.helpers import path_leaf

default_config_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../configs/config.json")
)
default_input_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../tests/data/isle-of-man-latest.osm.pbf")
)
#default_output_path = os.path.abspath(
#    os.path.join(os.path.dirname(__file__), "../outputs/example.geojson")
#)
logger = logging.getLogger(__name__)


@click.group()
def osmox():
    """
    Access cli.
    """
    pass


@osmox.command()
@click.argument("config_path", nargs=1, type=PathPath(exists=True), required=True)
def validate(config_path):
    """
    Validate a config.
    """
    cnfg = config.load(config_path)
    config.validate_activity_config(cnfg)
    logger.warning("Done.")


@osmox.command()
@click.argument('config_path', type=PathPath(exists=True), nargs=1, required=True)
@click.argument('input_path', type=PathPath(exists=True), nargs=1, required=True)
@click.argument('output_name', nargs=1, required=True)
@click.option("-crs", "--crs", type=str, default="epsg:27700",
              help="crs string eg (default): 'epsg:27700' (UK grid)")
@click.option("-s", "--single_use", is_flag=True,
              help="split multi-activity facilities into multiple single-activity facilities")
@click.option("-l", "--lazy", is_flag=True,
              help="if filtered object already has a label, do not search for more (supresses multi-use)")
def run(config_path, input_path, output_name, crs, single_use, lazy):
    logger.info(f" Loading config from {config_path}")
    cnfg = config.load(config_path)
    config.validate_activity_config(cnfg)

    #if not os.path.exists(output_path):
    #    logger.info(f'Creating output directory: {output_path}')
    #    os.mkdir(output_path)

    logger.info(f"Creating handler with crs: {crs}.")
    if single_use:
        logger.info("Handler is single-use, activities will get unique locations.")
    if lazy:
        logger.info("Handler will be using lazy assignment, this may suppress some multi-use.")

    handler = build.ObjectHandler(
        config=cnfg,
        crs=crs,
        lazy=lazy
        )
    logger.info(f" Filtering all objects found in {input_path}. This may take a long while.")
    handler.apply_file(str(input_path), locations=True, idx='flex_mem')
    logger.info(f" Found {len(handler.objects)} buildings.")
    logger.info(f" Found {len(handler.points)} nodes with valid tags.")
    logger.info(f" Found {len(handler.areas)} areas with valid tags.")

    logger.info(" Assigning object tags.")
    handler.assign_tags()
    logger.info(f" Finished assigning tags: f{handler.log}.")

    logger.info(" Assigning object activities.")
    handler.assign_activities()

    if cnfg.get("fill_missing_activities"):
        for group in cnfg["fill_missing_activities"]:
            logger.info(f" Filling missing activities: {group}.")
            zones, objects = handler.fill_missing_activities(
                area_tags=group["area_tags"],
                required_acts=group["required_acts"],
                new_tags=group["new_tags"],
                size=group["size"],
                spacing=group["spacing"]
            )
            logger.info(f" Filled {zones} zones with {objects} objects.")

    if cnfg.get("object_features"):
        logger.info(f" Assigning object features: {cnfg['object_features']}.")
        handler.add_features()

    if 'distance_to_nearest' in cnfg:
        for target_activity in cnfg["distance_to_nearest"]:
            logger.info(f" Assigning distances to nearest {target_activity}.")
            handler.assign_nearest_distance(target_activity)

    gdf = handler.geodataframe(single_use=single_use)

    path = path_leaf(input_path) / f"{output_name}_{crs.replace(':', '_')}.geojson"
    logger.info(f" Writting objects to: {path}")
    with open(path, "w") as file:
        file.write(gdf.to_json())

    if not crs == "epsg:4326":
        logger.info(" Reprojecting output to epsg:4326 (lat lon)")
        gdf.to_crs("epsg:4326", inplace=True)
        path = path_leaf(input_path) / f"{output_name}_epsg_4326.geojson"
        logger.info(f" Writting objects to: {path}")
        with open(path, "w") as file:
            file.write(gdf.to_json())

    logger.info("Done.")
