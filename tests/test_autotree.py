import os
from collections import defaultdict
from shapely.geometry import Point, Polygon
from osmbx import helpers, build

root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "data")
)
test_osm_path = os.path.join(root, "isle-of-man-latest.osm.pbf")


def test_autotree_insert():
    tree = helpers.AutoTree()
    facility = build.OSMObject(
            idx=0,
            activity_tags=[build.OSMTag(key="b", value="b")],
            geom=Point((10, 10))
            )
    tree.auto_insert(facility)
    assert len(tree.objects) == 1
    assert tree.counter == 1


def test_autotree_point_point_intersection():
    tree = helpers.AutoTree()
    target = build.OSMObject(
            idx=0,
            activity_tags=[build.OSMTag(key="b", value="b")],
            geom=Point((0, 0))
            )
    tree.auto_insert(
        target
    )
    tree.auto_insert(
        build.OSMObject(
            idx=0,
            activity_tags=[build.OSMTag(key="b", value="b")],
            geom=Point((10, 10))
            )
    )
    geom = Point((0, 0))
    assert tree.intersection(geom.bounds) == [target]


def test_autotree_point_poly_intersection():
    tree = helpers.AutoTree()
    target = build.OSMObject(
            idx=0,
            activity_tags=[build.OSMTag(key="b", value="b")],
            geom=Point((0, 0))
            )
    tree.auto_insert(target)
    tree.auto_insert(
        build.OSMObject(
            idx=0,
            activity_tags=[build.OSMTag(key="b", value="b")],
            geom=Point((10, 10))
            )
    )
    geom = Polygon([(-1, -1), (-1, 1), (1, 1), (1, -1), (-1, -1)])
    assert tree.intersection(geom.bounds) == [target]


def test_autotree_poly_poly_intersection():
    tree = helpers.AutoTree()
    target = build.OSMObject(
            idx=0,
            activity_tags=[build.OSMTag(key="b", value="b")],
            geom=Polygon([(-2, -1), (-2, 1), (0, 1), (0, -1), (-2, -1)])
            )
    tree.auto_insert(target)
    tree.auto_insert(
        build.OSMObject(
            idx=0,
            activity_tags=[build.OSMTag(key="b", value="b")],
            geom=Point((10, 10))
            )
    )
    geom = Polygon([(-1, -1), (-1, 1), (1, 1), (1, -1), (-1, -1)])
    assert tree.intersection(geom.bounds) == [target]


def test_autotree_iter():
    tree = helpers.AutoTree()
    for i in range(3):
        tree.auto_insert(
        build.OSMObject(
            idx=0,
            activity_tags=[build.OSMTag(key="b", value="b")],
            geom=Point((10, 10))
            )
    )
    out = [o for o in tree]
    assert len(out) == 3
