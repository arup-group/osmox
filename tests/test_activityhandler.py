import os
import pytest
from shapely.geometry import Point, Polygon
import geopandas as gp

from osmox import config, build, helpers

fixtures_root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "fixtures")
)
toy_osm_path = os.path.join(fixtures_root, "toy.osm")
test_osm_path = os.path.join(fixtures_root, "toy_selection.osm")
test_config_path = os.path.join(fixtures_root, "test_config.json")


@pytest.fixture()
def test_config():
    return config.load(test_config_path)


def test_innit(test_config):
    assert build.ObjectHandler(test_config)


@pytest.fixture()
def testHandler(test_config):
    return build.ObjectHandler(test_config)


def test_object_assign_points():
    
    building = build.Object(
        idx="XL",
        osm_tags={"building":"yes"},
        activity_tags=[],
        geom=Polygon([(-5, -5), (-5, 5), (5, 5), (5, -5), (-5, -5)])
        )
    tree = helpers.AutoTree()
    tree.auto_insert(
            build.OSMObject(
            idx=0,
            activity_tags=[build.OSMTag(key="a", value="a")],
            geom=Point((0, 0))
            )
        )
    tree.auto_insert(
        build.OSMObject(
            idx=0,
            activity_tags=[build.OSMTag(key="b", value="b")],
            geom=Point((10, 10))
            )
        )
    tree.auto_insert(
        build.OSMObject(
            idx=0,
            activity_tags=[
                build.OSMTag(key="c", value="c"),
                build.OSMTag(key="d", value="d")
                ],
            geom=Point((1, -1))
            )
        )
    assert building.assign_points(tree)
    assert building.activity_tags == [
        build.OSMTag(key='a', value='a'),
        build.OSMTag(key='c', value='c'),
        build.OSMTag(key='d', value='d')
        ]


def test_object_assign_areas():
    
    building = build.Object(
        idx="XL",
        osm_tags={"building":"yes"},
        activity_tags=[],
        geom=Polygon([(-5, -5), (-5, 5), (5, 5), (5, -5), (-5, -5)])
        )
    tree = helpers.AutoTree()
    tree.auto_insert(
            build.OSMObject(
            idx=0,
            activity_tags=[build.OSMTag(key="a", value="a")],
            geom=Polygon([(-5, -5), (-5, 5), (5, 5), (5, -5), (-5, -5)])
            )
        )
    tree.auto_insert(
        build.OSMObject(
            idx=0,
            activity_tags=[build.OSMTag(key="b", value="b")],
            geom=Polygon([(10, 10), (10, 25), (25, 25), (25, 10), (10, 10)])
            )
        )
    tree.auto_insert(
        build.OSMObject(
            idx=0,
            activity_tags=[
                build.OSMTag(key="c", value="c"),
                build.OSMTag(key="d", value="d")
                ],
            geom=Polygon([(-50, -50), (-50, 50), (50, 50), (50, -50), (-50, -50)])
            )
        )
    assert building.assign_points(tree)
    assert building.activity_tags == [
        build.OSMTag(key='a', value='a'),
        build.OSMTag(key='c', value='c'),
        build.OSMTag(key='d', value='d')
        ]


def test_load_toy(testHandler):
    handler = testHandler
    handler.apply_file(toy_osm_path, locations=True, idx='flex_mem')
    assert len(handler.objects) == 5
    assert len(handler.points) == 6
    assert len(handler.areas) == 2