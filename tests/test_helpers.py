import geopandas as gpd
import pytest
from geopandas.testing import assert_geodataframe_equal
from osmox import helpers
from shapely.geometry import Polygon


@pytest.mark.parametrize(
    "a,b,expected",
    [
        ((), (), False),
        (((), ()), (), False),
        (((1, 2)), (), False),
        (((1, 1), ()), (), False),
        (((1, 1), (2, 2), (3, 3)), ((1, 1), (2, 2), (3, 3)), True),
        (((2, 2), (3, 3)), ((1, 1), (2, 2)), True),
        (((1, 2), (3, 3)), ((1, 1), (2, 1)), False),
        (((1, 1), (1, 2), (3, 3)), ((1, 3), (1, 2), (4, 3)), True),
    ],
)
def test_tag_matches(a, b, expected):
    assert helpers.tag_match(a, b) == expected


@pytest.mark.parametrize(
    "area,spacing,expected",
    [
        (Polygon([(0, 0), (0, 50), (50, 50), (50, 0), (0, 0)]), [100, 100], [(0, 0)]),
        (Polygon([(0, 0), (0, 50), (50, 50), (50, 0), (0, 0)]), [51, 51], [(0, 0)]),
        (
            Polygon([(0, 0), (0, 50), (50, 50), (50, 0), (0, 0)]),
            [50, 50],
            [(0, 0), (0, 50), (50, 0), (50, 50)],
        ),
        (
            Polygon([(0, 0), (0, 50), (10, 50), (10, 0), (0, 0)]),
            [25, 25],
            [(0, 0), (0, 25), (0, 50)],
        ),
    ],
)
def test_build_bounding_box_grid_from_areas(area, spacing, expected):
    assert set(helpers.bounding_grid(area=area, spacing=spacing)) == set(expected)


@pytest.mark.parametrize(
    "area,spacing,expected",
    [
        (Polygon([(0, 0), (0, 50), (50, 50), (0, 0)]), [100, 100], [(0, 0)]),
        (Polygon([(0, 0), (0, 50), (50, 50), (0, 0)]), [51, 51], [(0, 0)]),
        (
            Polygon([(0, 0), (0, 50), (50, 50), (0, 0)]),
            [50, 50],
            [(0, 0), (0, 50), (50, 50)],
        ),
        (
            Polygon([(0, 0), (0, 50), (10, 50), (0, 0)]),
            [25, 25],
            [(0, 0), (0, 25), (0, 50)],
        ),
    ],
)
def test_build_area_grid_from_areas(area, spacing, expected):
    assert set(helpers.area_grid(area=area, spacing=spacing)) == set(expected)


def test_fill_objects():
    p = (0, 0)
    obj = helpers.fill_object(
        0, p, [10, 10], [["osm_tag", 1]], [["new_tags", 2]], ["act"]
    )
    assert obj.geom.equals(Polygon([(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)]))
    assert obj.idx == "fill_0"
    assert obj.activities == ["act"]


def test_point_to_poly():
    p = (0, 0)
    poly = helpers.point_to_poly(p, [10, 10])
    assert poly.equals(Polygon([(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)]))


@pytest.mark.parametrize("inp,expected", [("2", 2.0), ("4m", 4.0), ("2ft", 6.0)])
def test_height_to_m(inp, expected):
    assert helpers.height_to_m(inp) == expected


@pytest.mark.parametrize(
    "inp,expected", [("1'", round(12 / 39.3701, 3)), ("1'1\"", round(13 / 39.3701, 3))]
)
def test_imperial_to_metric(inp, expected):
    assert helpers.imperial_to_metric(inp) == expected


@pytest.fixture(params=["GeoJSON", "GPKG", "parquet"])
def file_format_data(tmp_path, request):
    gdf = gpd.GeoDataFrame(
        geometry=gpd.points_from_xy(x=[0, 1, 0, 1], y=[0, 0, 1, 1], crs="epsg:27700")
    )
    kwargs = {}
    if request.param == "parquet":
        func = "to_parquet"
    else:
        func = "to_file"
        kwargs["driver"] = request.param
    filepath = tmp_path / f"test_{request.param}.{request.param.lower()}"
    getattr(gdf, func)(filepath, **kwargs)

    return filepath, gdf


def test_read_geofile(file_format_data):
    filepath, gdf = file_format_data
    new_gdf = helpers.read_geofile(filepath)
    assert_geodataframe_equal(gdf, new_gdf)
