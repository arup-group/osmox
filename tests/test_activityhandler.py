import os

import geopandas as gpd
import pytest
from osmox import build, config, helpers
from shapely.geometry import Point, Polygon

fixtures_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures"))
toy_osm_path = os.path.join(fixtures_root, "toy.osm")
park_osm_path = os.path.join(fixtures_root, "park.osm")
test_osm_path = os.path.join(fixtures_root, "toy_selection.osm")
test_config_path = os.path.join(fixtures_root, "test_config.json")
leisure_config_path = os.path.join(fixtures_root, "test_config_leisure.json")


@pytest.fixture()
def test_config():
    return config.load(test_config_path)


def test_innit(test_config):
    assert build.ObjectHandler(test_config)


@pytest.fixture()
def testHandler(test_config):
    return build.ObjectHandler(test_config, crs="epsg:4326")


def test_object_assign_points():

    building = build.Object(
        idx="XL",
        osm_tags={"building": "yes"},
        activity_tags=[],
        geom=Polygon([(-5, -5), (-5, 5), (5, 5), (5, -5), (-5, -5)]),
    )
    tree = helpers.AutoTree()
    tree.auto_insert(
        build.OSMObject(idx=0, activity_tags=[build.OSMTag(key="a", value="a")], geom=Point((0, 0)))
    )
    tree.auto_insert(
        build.OSMObject(
            idx=0, activity_tags=[build.OSMTag(key="b", value="b")], geom=Point((10, 10))
        )
    )
    tree.auto_insert(
        build.OSMObject(
            idx=0,
            activity_tags=[build.OSMTag(key="c", value="c"), build.OSMTag(key="d", value="d")],
            geom=Point((1, -1)),
        )
    )
    assert building.assign_points(tree)
    assert building.activity_tags == [
        build.OSMTag(key="a", value="a"),
        build.OSMTag(key="c", value="c"),
        build.OSMTag(key="d", value="d"),
    ]


def test_object_assign_areas():

    building = build.Object(
        idx="XL",
        osm_tags={"building": "yes"},
        activity_tags=[],
        geom=Polygon([(-5, -5), (-5, 5), (5, 5), (5, -5), (-5, -5)]),
    )
    tree = helpers.AutoTree()
    tree.auto_insert(
        build.OSMObject(
            idx=0,
            activity_tags=[build.OSMTag(key="a", value="a")],
            geom=Polygon([(-5, -5), (-5, 5), (5, 5), (5, -5), (-5, -5)]),
        )
    )
    tree.auto_insert(
        build.OSMObject(
            idx=0,
            activity_tags=[build.OSMTag(key="b", value="b")],
            geom=Polygon([(10, 10), (10, 25), (25, 25), (25, 10), (10, 10)]),
        )
    )
    tree.auto_insert(
        build.OSMObject(
            idx=0,
            activity_tags=[build.OSMTag(key="c", value="c"), build.OSMTag(key="d", value="d")],
            geom=Polygon([(-50, -50), (-50, 50), (50, 50), (50, -50), (-50, -50)]),
        )
    )
    assert building.assign_points(tree)
    assert building.activity_tags == [
        build.OSMTag(key="a", value="a"),
        build.OSMTag(key="c", value="c"),
        build.OSMTag(key="d", value="d"),
    ]


def test_load_toy(testHandler):
    handler = testHandler
    handler.apply_file(toy_osm_path, locations=True, idx="flex_mem")
    assert len(handler.objects) == 5
    assert len(handler.points) == 6
    assert len(handler.areas) == 3


@pytest.fixture()
def test_leisure_config():
    return config.load(leisure_config_path)


@pytest.fixture()
def leisureHandler(test_leisure_config):
    return build.ObjectHandler(test_leisure_config, crs="epsg:4326", lazy=False)


def test_leisure_handler(leisureHandler):
    handler = leisureHandler
    handler.apply_file(park_osm_path, locations=True, idx="flex_mem")
    handler.assign_tags()
    handler.assign_activities()
    df = handler.geodataframe(single_use=True)
    assert "leisure" in set(df.activity)


class TestAreaActIntersection:
    @pytest.fixture
    def updated_handler(self, testHandler):
        testHandler.add_object(
            idx=0,
            activity_tags=[["test_tag", "test_value"]],
            osm_tags=[["test", "test"]],
            geom=Polygon([(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)]),
        )
        testHandler.add_object(
            idx=0,
            activity_tags=[["test_tag", "test_value"]],
            osm_tags=[["test", "test"]],
            geom=Point((1, 1)),
        )
        testHandler.add_object(
            idx=0,
            activity_tags=[["test_tag", "test_value"]],
            osm_tags=[["test", "test"]],
            geom=Point((100, 100)),
        )
        for o, acts in zip(testHandler.objects, [["a"], ["b", "c"], ["d"]]):
            o.activities = acts
        return testHandler

    @pytest.fixture
    def get_required_activities_in_target(self, updated_handler):
        def _get_required_activities_in_target(required_activities):
            return updated_handler._required_activities_in_target(
                required_activities, Polygon([(0, 0), (0, 50), (50, 50), (50, 0), (0, 0)]), (10, 10)
            )

        return _get_required_activities_in_target

    def test_activities_from_area_intersection(self, updated_handler):

        acts = updated_handler._activities_from_area_intersection(
            Polygon([(0, 0), (0, 50), (50, 50), (50, 0), (0, 0)]), (10, 10)
        )
        assert acts == {
            "a": [Polygon([(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)])],
            "b": [Polygon([(1, 1), (11, 1), (11, 11), (1, 11), (1, 1)])],
            "c": [Polygon([(1, 1), (11, 1), (11, 11), (1, 11), (1, 1)])],
        }

    def test_required_activities_one_in_target(self, get_required_activities_in_target):
        geom_list = get_required_activities_in_target(["a"])
        assert geom_list == [Polygon([(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)])]

    def test_required_activities_two_in_target(self, get_required_activities_in_target):
        geom_list = get_required_activities_in_target(["a", "b"])
        assert geom_list == [
            Polygon([(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)]),
            Polygon([(1, 1), (11, 1), (11, 11), (1, 11), (1, 1)]),
        ]

    def test_required_activities_one_in_one_out_target(self, get_required_activities_in_target):
        geom_list = get_required_activities_in_target(["b", "d"])
        assert geom_list == [Polygon([(1, 1), (11, 1), (11, 11), (1, 11), (1, 1)])]

    def test_required_activities_one_out_target(self, get_required_activities_in_target):
        geom_list = get_required_activities_in_target(["d"])
        assert not geom_list


class TestMissingActivity:

    @pytest.fixture(scope="function")
    def updated_handler(self, testHandler):
        testHandler.add_object(
            idx=0,
            activity_tags=[["test_tag", "test_value"]],
            osm_tags=[["test", "test"]],
            geom=Polygon([(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)]),
        )
        testHandler.add_object(
            idx=0,
            activity_tags=[["test_tag", "test_value"]],
            osm_tags=[["test", "test"]],
            geom=Point((1, 1)),
        )
        testHandler.add_object(  # not in area
            idx=0,
            activity_tags=[["test_tag", "test_value"]],
            osm_tags=[["test", "test"]],
            geom=Point((110, 110)),
        )
        testHandler.add_area(
            idx=0,
            activity_tags=[["landuse", "residential"]],
            geom=Polygon([(0, 0), (0, 100), (100, 100), (100, 0), (0, 0)]),
        )
        for o, acts in zip(testHandler.objects, [["a"], ["b", "c"], ["d"]]):
            o.activities = acts
        return testHandler

    @pytest.fixture
    def point_source_filepath(self, tmp_path):

        gdf = gpd.GeoDataFrame(
            geometry=gpd.points_from_xy(x=[0, 1, 10, 200], y=[0, 101, 20, 1], crs="epsg:4326")
        )
        filepath = tmp_path / "point_source.parquet"
        gdf.to_parquet(filepath)
        return filepath

    @pytest.fixture
    def updated_handler_with_required_act_geoms(self, updated_handler):
        "Total default area: 300 units, compared to 10000 units for the target area (i.e. 0.03)"
        updated_handler.add_object(
            idx=0,
            activity_tags=[["test_tag", "test_value"]],
            osm_tags=[["test", "test"]],
            geom=Point((1, 1)),  # area: size[0] * size[1]
        )
        updated_handler.add_object(
            idx=0,
            activity_tags=[["test_tag", "test_value"]],
            osm_tags=[["test", "test"]],
            geom=Polygon([(30, 40), (30, 60), (40, 60), (40, 40), (30, 40)]),  # area: 200 units
        )
        for object in updated_handler.objects:
            if object.activities is None:
                object.activities = ["d"]

        return updated_handler

    def test_fill_missing_activities_single_building(self, updated_handler):

        updated_handler.fill_missing_activities(
            area_tags=[("landuse", "residential")],
            required_acts="d",
            new_tags=[("building", "house")],
            size=(10, 10),
            spacing=(101, 101),
        )

        objects = [o for o in updated_handler.objects]
        house = objects[-1]
        assert house.idx == "fill_0"
        assert house.geom.equals(Polygon([(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)]))

    def test_fill_missing_activities_multiple_buildings(self, updated_handler):

        updated_handler.fill_missing_activities(
            area_tags=[("landuse", "residential")],
            required_acts="d",
            new_tags=[("building", "house")],
            size=(10, 10),
            spacing=(100, 100),
        )

        objects = [o for o in updated_handler.objects]
        house = objects[-4]
        assert house.idx == "fill_0"
        assert house.geom.equals(Polygon([(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)]))
        house = objects[-1]
        assert house.idx == "fill_3"
        assert house.geom.equals(
            Polygon(
                [(100.0, 100.0), (110.0, 100.0), (110.0, 110.0), (100.0, 110.0), (100.0, 100.0)]
            )
        )

    def test_fill_missing_activities_data_point_source(
        self, updated_handler, point_source_filepath
    ):
        updated_handler.fill_missing_activities(
            area_tags=[("landuse", "residential")],
            required_acts="d",
            new_tags=[("building", "house")],
            size=(10, 10),
            fill_method="point_source",
            point_source=point_source_filepath,
        )

        objects = [o for o in updated_handler.objects]

        house_1 = objects[-2]
        assert house_1.idx == "fill_0"
        assert house_1.geom.equals(Polygon([(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)]))

        house_2 = objects[-1]
        assert house_2.idx == "fill_1"
        assert house_2.geom.equals(
            Polygon([(10.0, 20.0), (20.0, 20.0), (20.0, 30.0), (10.0, 30.0), (10.0, 20.0)])
        )

    def test_fill_missing_activities_data_point_source_missing(self, updated_handler):
        with pytest.raises(
            ValueError,
            match="Missing activity fill method expects a path to a point source geospatial data file, received None",
        ):
            updated_handler.fill_missing_activities(
                area_tags=[("landuse", "residential")],
                required_acts="d",
                new_tags=[("building", "house")],
                size=(10, 10),
                fill_method="point_source",
            )

    @pytest.mark.parametrize(
        ["max_fraction", "expected_fill"], [(0, False), (0.02, False), (0.04, True)]
    )
    def test_fill_missing_activities_max_existing_acts_fraction(
        self, updated_handler_with_required_act_geoms, max_fraction, expected_fill
    ):
        updated_handler_with_required_act_geoms.fill_missing_activities(
            area_tags=[("landuse", "residential")],
            required_acts="d",
            new_tags=[("building", "house")],
            size=(10, 10),
            spacing=(100, 100),
            fill_method="spacing",
            max_existing_acts_fraction=max_fraction,
        )

        objects = [o for o in updated_handler_with_required_act_geoms.objects]
        has_fill = any(
            isinstance(house.idx, str) and house.idx.startswith("fill") for house in objects
        )
        assert has_fill is expected_fill


class TestExtract:

    @pytest.fixture(scope="function")
    def updated_handler(self, testHandler):
        testHandler.add_object(
            idx=0,
            activity_tags=[["a", "b"]],
            osm_tags=[["a", "b"]],
            geom=Polygon([(-5, -5), (-5, 5), (5, 5), (5, -5), (-5, -5)]),
        )
        testHandler.objects.objects[0].activities = ["a", "b"]
        testHandler.objects.objects[0].features = {"feature": 0}
        return testHandler

    def test_extract_multiuse_object_geodataframe(self, updated_handler):
        gdf = updated_handler.geodataframe()
        assert len(gdf) == 1
        obj = gdf.iloc[0].to_dict()
        assert obj["activities"] == "a,b"
        assert obj["geometry"] == Point(0, 0)
        assert obj["id"] == 0
        assert obj["feature"] == 0

    def test_extract_single_use_object_geodataframe(self, updated_handler):
        gdf = updated_handler.geodataframe(single_use=True)
        assert len(gdf) == 2
        gdf.iloc[0].to_dict()["activity"] == "a"
        gdf.iloc[1].to_dict()["activity"] == "b"
        for i in range(2):
            obj = gdf.iloc[i].to_dict()
            assert obj["geometry"] == Point(0, 0)
            assert obj["id"] == 0
            assert obj["feature"] == 0
