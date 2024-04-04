import logging
from pathlib import Path
from typing import Union

import click
import geopandas as gp
from rtree import index
from shapely.geometry import Point, Polygon

from osmox import build

logger = logging.getLogger(__name__)


class PathPath(click.Path):
    """A Click path argument that returns a pathlib Path, not a string"""

    def convert(self, value, param, ctx):
        return Path(super().convert(value, param, ctx))


class AutoTree(index.Index):
    """
    Spatial bounding box transforming (using pyproj) and indexing (using Rtree).
    """

    def __init__(self):
        super().__init__()
        self.objects = []
        self.counter = 0

    def auto_insert(self, object):
        super().insert(self.counter, object.geom.bounds)
        self.objects.append(object)
        self.counter += 1

    def intersection(self, coordinates):
        ids = super().intersection(coordinates, objects=False)
        return [self.objects[i] for i in ids]

    def __iter__(self):
        for o in self.objects:
            yield o

    def __len__(self):
        return self.counter

    def __str__(self):
        print(list(self))


def dict_list_match(d, dict_list):
    """
    Check if simple key value pairs from dict d are in dictionary of lists.
    eg:
    dict_list_match({1:2}, {1:[1,2,3]}) == True
    dict_list_match({1:4}, {1:[1,2,3]}) == False
    dict_list_match({2:1}, {1:[1,2,3]}) == False
    """
    for k, v in d.items():
        viable = dict_list.get(k, [])
        if v in viable or viable == "*":
            return True
    return False


def height_to_m(height):
    """
    Parse height to float in metres.
    """
    height.strip()

    if is_string_float(height):
        return float(height)

    if "m" in height:
        height = height.replace("m", "")
        if is_string_float(height):
            return float(height)

    if "ft" in height:
        height = height.replace("ft", "")
        if is_string_float(height):
            return float(height) * 3

    if "'" in height:
        return imperial_to_metric(height)

    logger.warning(f"Unable to convert height {height} to metres, returning 3")
    return 3.0


def is_string_float(number):
    try:
        float(number)
        return True
    except ValueError:
        return False


def imperial_to_metric(height):
    """
    Convert imperial (feet and inches) to metric (metres).
    Expect formatted as 3'4" (3 feet and 4 inches) or 3' (3 feet).
    Return float
    """
    inches = float(height.split("'")[0].strip()) * 12
    if '"' in height:
        inches += float(height.split("'")[-1].replace('"', "").strip())
    return round(inches / 39.3701, 3)


def progressBar(iterable, prefix="", suffix="", decimals=1, length=100, fill="|", printEnd="\r"):
    """
    from here: https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    total = len(iterable)

    # Progress Bar Printing Function
    def printProgressBar(iteration):
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + "-" * (length - filledLength)
        print(f"\r{prefix} |{bar}| {percent}% {suffix}", end=printEnd)

    # Initial Call
    printProgressBar(0)
    # Update Progress Bar
    for i, item in enumerate(iterable):
        yield item
        printProgressBar(i + 1)
    # Print New Line on Complete
    print()


def get_distance(p):
    """
    Return the distance between two shapely points
    Assumes orthogonal projection in meters
    :params tuple p: A tuple conctaining two Shapely points

    :return float: Distance in meters
    """
    distance = ((p[0].x - p[1].x) ** 2 + (p[0].y - p[1].y) ** 2) ** 0.5
    return distance


def tag_match(a, b):
    if not len(a):
        return False
    if not len(b):
        return False
    for ka, va in a:
        for kb, vb in b:
            if ka == kb and va == vb:
                return True
    return False


def bounding_grid(area, spacing):
    grid = []
    min_x, min_y, max_x, max_y = area.bounds
    nxs = 1 + int((max_x - min_x) / spacing[0])
    nys = 1 + int((max_y - min_y) / spacing[1])
    for ix in range(0, nxs):
        x = min_x + (ix * spacing[0])
        for iy in range(0, nys):
            y = min_y + (iy * spacing[1])
            grid.append((x, y))
    return grid


def area_grid(area, spacing):
    grid = bounding_grid(area, spacing)
    return [p for p in grid if area.intersects(Point(p))]


def fill_object(i, point, size, new_osm_tags, new_tags, required_acts):
    geom = point_to_poly(point, size)
    idx = f"fill_{i}"
    object = build.Object(idx=idx, osm_tags=new_osm_tags, activity_tags=new_tags, geom=geom)
    object.activities = list(required_acts)
    return object


def point_to_poly(point: tuple[float, float], size: tuple[float, float]) -> Polygon:
    dx, dy = size[0], size[1]
    x, y = point
    geom = Polygon([(x, y), (x + dx, y), (x + dx, y + dy), (x, y + dy), (x, y)])
    return geom


def path_leaf(filepath):
    folder_path = Path(filepath).parent
    return folder_path


def read_geofile(filepath: Union[str, Path]) -> gp.GeoDataFrame:
    filepath_extension = Path(filepath).suffixes
    if ".parquet" in filepath_extension:
        return gp.read_parquet(filepath)
    else:
        return gp.read_file(filepath)
