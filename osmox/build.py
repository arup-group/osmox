import json
import pandas as pd
import geopandas as gp
from collections import defaultdict
import osmium
import shapely.wkb as wkblib
import logging
from collections import namedtuple
from pyproj import Proj, Transformer, CRS
from shapely.ops import transform, nearest_points
from shapely.geometry import Point, Polygon, MultiPoint


from osmox import config, helpers


OSMTag = namedtuple('OSMtag', 'key value')
OSMObject = namedtuple('OSMobject', 'idx, activity_tags, geom')
AVAILABLE_FEATURES = [
    "area",
    "levels",
    "floor_area",
    "units",
    "transit_distance"
]

class Object:

    DEFAULT_LEVELS = {  # for if a level tag is required but not found
        "apartments": 4,
        "bungalow": 1,
        "detached": 2,
        "dormitory": 4,
        "hotel": 3,
        "house": 2,
        "residential": 2,
        "semidetached_house": 2,
        "terrace": 2,
        "commercial": 1,
        "retail": 1,
        "supermarket": 1,
        "industrial": 1,
        "office": 4,
        "warehouse": 1,
        "bakehouse": 1,
        "firestation": 2,
        "government": 2,
        "cathedral": 1,
        "chapel": 1,
        "church": 1,
        "mosque": 1,
        "religous": 1,
        "shrine": 1,
        "synagogue": 1,
        "temple": 1,
        "hospital": 4,
        "kindergarden": 2,
        "school": 2,
        "university": 3,
        "college": 3,
        "sports_hall": 1,
        "stadium": 1
    }
    
    def __init__(self, idx, osm_tags, activity_tags, geom) -> None:
        self.idx = idx
        self.osm_tags = dict(osm_tags)
        self.activity_tags = activity_tags
        self.geom = geom
        self.activities = None
        self.features = {}


    def add_features(self, features):
        available = {
            "area": self.area,
            "levels": self.levels,
            "floor_area": self.floor_area,
            "units": self.units,
        }
        for f in features:
            self.features[f] = available[f]()

    def area(self):
        return int(self.geom.area)

    def levels(self):
        if 'building:levels' in self.osm_tags:
            levels = self.osm_tags['building:levels']
            if levels.isnumeric():
                return float(levels)  # todo ensure integer
        if 'height' in self.osm_tags:
            height = helpers.height_to_m(self.osm_tags['height'])
            if height:
                return float(height / 4)
        if self.osm_tags.get("building"):
            if self.osm_tags["building"] in self.DEFAULT_LEVELS:
                return self.DEFAULT_LEVELS[self.osm_tags["building"]]
            return 2
        return 1

    def floor_area(self):
        return self.area() * self.levels()

    def units(self):
        if 'building:flats' in self.osm_tags:
            return int(self.osm_tags['building:flats'])
        return 1

    def __str__(self):
        return f"""
            {self.__class__}: 
            id: {self.idx}
            osm_tags: {self.osm_tags}
            activity_tags: {self.activity_tags}
            activities: {self.activities}
            geom: {self.geom}
            """

    def add_tags(self, osm_objects):
        for o in osm_objects:
            if o.activity_tags:
                self.activity_tags.extend(o.activity_tags)

    def apply_default_tag(self, tag):
        self.activity_tags = [OSMTag(tag[0], tag[1])]

    def assign_points(self, points):
        snaps = [c for c in points.intersection(self.geom.bounds)]
        if snaps:
            self.add_tags(snaps)
            return True

    def assign_areas(self, areas):
        snaps = [c for c in areas.intersection(self.geom.bounds)]
        snaps = [c for c in snaps if c.geom.contains(self.geom.centroid)]
        if snaps:
            self.add_tags(snaps)
            return True

    def assign_activities(self, activity_lookup, weight_calculations=None):
        """
        Create a list of unique activities based on activity tags.
        This method is currently kept here incase we want to deal with 
        duplicate assignments differently in future.
        """
        act_set = set()
        for tag in self.activity_tags:
            act_set |= set(activity_lookup.get(tag.key,{}).get(tag.value,[]))
        self.activities = list(act_set)

    def get_closest_distance(self, targets, name):
        """
        Calculate euclidean distance to nearest target
        :params Multipoint targets: A Shapely Multipoint object of all targets
        """
        if not targets:
            self.features[f"distance_to_nearest_{name}"] = None
        else:
            nearest = nearest_points(self.geom.centroid, targets)
            self.features[f"distance_to_nearest_{name}"] = helpers.get_distance(nearest)

    # @property
    def transit_distance(self):
        return self._transit_distance

    def summary(self):
        """
        Returbn a dict summary.
        """
        fixed = {
            "id": self.idx,
            "activities": ','.join(self.activities),
            "geometry": self.geom.centroid
        }
        return {**fixed, **self.features}

    def single_activity_summaries(self):
        """
        Yield (dict) summaries for each each activity of an object.
        """
        for act in self.activities:
            fixed = {
                "id": self.idx,
                "activity": act,
                "geometry": self.geom.centroid
            }
            yield {**fixed, **self.features}


class ObjectHandler(osmium.SimpleHandler):

    wkbfab = osmium.geom.WKBFactory()
    logger = logging.getLogger(__name__)

    def __init__(self, config, crs='epsg:27700', from_crs='epsg:4326', level=logging.DEBUG):

        super().__init__()
        logging.basicConfig(level=level)
        self.cnfg = config
        self.crs = crs
        self.filter = self.cnfg["filter"]
        self.object_features = self.cnfg["object_features"]
        self.default_tags = self.cnfg["default_tags"]
        self.activity_config = self.cnfg["activity_mapping"]
        self.transformer = Transformer.from_crs(CRS(from_crs), CRS(crs), always_xy=True)

        self.objects = helpers.AutoTree()
        self.points = helpers.AutoTree()
        self.areas = helpers.AutoTree()

        self.log = {
            "existing": 0,
            "points": 0,
            "areas": 0,
            "defaults": 0
            }

    """
    On handler.apply_file() method; parse through all nodes and areas:
    (i) add them to self.objects if they are within the filter_config
    (ii) else, add them to self.areas or self.points if they are within the activity_mapping
    """

    def selects(self, tags):
        if tags:
            tags = dict(tags)
            return helpers.dict_list_match(tags, self.filter)

    def get_filtered_tags(self, tags):
        """
        Return configured activity tags for an OSM object as list of OSMtags.
        """
        if tags:
            tags = dict(tags)
            found = []
            for osm_key, osm_val in tags.items():
                if osm_key in self.activity_config:
                    if osm_val in self.activity_config[osm_key] or self.activity_config[osm_key] == "*":
                        found.append(OSMTag(key=osm_key, value=osm_val))
            return found

    def add_object(self, idx, activity_tags, osm_tags, geom):
        if geom:
            geom = transform(self.transformer.transform, geom)
            self.objects.auto_insert(Object(idx=idx, osm_tags=osm_tags, activity_tags=activity_tags, geom=geom))

    def add_point(self, idx, activity_tags, geom):
        if geom:
            geom = transform(self.transformer.transform, geom)
            self.points.auto_insert(OSMObject(idx=idx, activity_tags=activity_tags, geom=geom))

    def add_area(self, idx, activity_tags, geom):
        if geom:
            geom = transform(self.transformer.transform, geom)
            self.areas.auto_insert(OSMObject(idx=idx, activity_tags=activity_tags, geom=geom))

    def fab_point(self, n):
        try:
            wkb = self.wkbfab.create_point(n)
            return wkblib.loads(wkb, hex=True)
        except RuntimeError:
            self.logger.warning(f' RuntimeError encountered for point: {n}')
            return None

    def fab_area(self, a):
        try:
            wkb = self.wkbfab.create_multipolygon(a)
            return wkblib.loads(wkb, hex=True)
        except RuntimeError:
            self.logger.warning(f' RuntimeError encountered for polygon: {a}')
            return None

    def node(self, n):
        activity_tags = self.get_filtered_tags(n.tags)
        # todo consider renaming activiity tags to filtered or selected tags
        if self.selects(n.tags):
            self.add_object(idx=n.id, osm_tags=n.tags, activity_tags=activity_tags, geom=self.fab_point(n))
        elif activity_tags:
            self.add_point(idx=n.id, activity_tags=activity_tags, geom=self.fab_point(n))

    def area(self, a):
        activity_tags = self.get_filtered_tags(a.tags)
        if self.selects(a.tags):
            self.add_object(idx=a.id, osm_tags=a.tags, activity_tags=activity_tags, geom=self.fab_area(a))
        elif activity_tags:
            self.add_area(idx=a.id, activity_tags=activity_tags, geom=self.fab_area(a))

    """
    Assign unknown tags to buildings spatially.
    """

    def assign_tags(self):

        for obj in helpers.progressBar(self.objects, prefix = 'Progress:', suffix = 'Complete', length = 50):

            if obj.activity_tags:
                # if an onject already has activity tags, continue
                self.log["existing"] += 1
                continue

            if obj.assign_points(self.points):
                # else try to assign activity tags based on contained point objects
                self.log["points"] += 1
                continue

            if obj.assign_areas(self.areas):
                # else try to assign activity tags based on containing area objects
                self.log["areas"] += 1
                continue
            
            if self.default_tags:
                # otherwise apply defaults if set
                self.log["defaults"] += 1
                for a in self.default_tags:
                    obj.apply_default_tag(a)

    def assign_activities(self):
        for obj in helpers.progressBar(self.objects, prefix = 'Progress:', suffix = 'Complete', length = 50):
            obj.assign_activities(self.activity_config)


    def fill_missing_activities(
        self,
        area_tags=(("landuse", "residential")),
        required_acts=("home"),
        new_tags=(("building", "house")),
        size=(10, 10), spacing=(25, 25)
        ):
        """
        Fill "empty" areas with new objects. Empty areas are defined as areas with the select_tags but
        not containing any objects of the required_acts.
        An example of such missing objects would be missing home facilities in a residential area.
        Empty areas are filled with new objects of given size at given spacing.

        Args:
            area_tags (tuple, optional): Defines (any) osm tags of areas to be considered. Defaults to (("landuse", "residential")).
            required_acts (tuple, optional): Expected (any) object activity types to be found in areas. Defaults to ("home").
            new_tags (tuple, optional): Tags for new objects. Defaults to (("building", "house")).
            size (tuple, optional): x,y dimensions of new object polygon. Defaults to (10, 10).
            spacing (tuple, optional): x,y dimensions of new objects spacing. Defaults to (25, 25).

        Returns:
            int, int: number of empty zones, number of new objects
        """

        empty_zones = 0  # conuter for fill zones
        i = 0  # counter for object id
        new_osm_tags = [OSMTag(key=k, value=v) for k, v in area_tags]
        new_tags = [OSMTag(key=k, value=v) for k, v in new_tags]

        for area in helpers.progressBar(self.areas, prefix = 'Progress:', suffix = 'Complete', length = 50):

            if not helpers.tag_match(a=area_tags, b=area.activity_tags):
                continue

            if self.required_activities_in_target(required_acts, area.geom):
                continue

            empty_zones += 1  # increment another empty zone

            # sample a grid
            points = helpers.area_grid(area=area.geom, spacing=spacing)
            for point in points:  # add objects built from grid
                self.objects.auto_insert(helpers.fill_object(i, point, size, new_osm_tags, new_tags, required_acts))
                i += 1

        return empty_zones, i

    def required_activities_in_target(self, required_activities, target):
        found_activities = self.activities_from_area_intersection(target)
        return set(required_activities) & found_activities  # in both

    def activities_from_area_intersection(self, target):
        objects = self.objects.intersection(target.bounds)
        objects = [o for o in objects if target.contains(o.geom)]
        return set([act for object in objects for act in object.activities])

    def add_features(self):
        """
        ["units", "floors", "area", "floor_area"]
        """
        for obj in helpers.progressBar(self.objects, prefix = 'Progress:', suffix = 'Complete', length = 50):
            obj.add_features(self.object_features)

    def assign_nearest_distance(self, target_act):
        """
        For each facility, calculate euclidean distance to targets of given activity type.
        """
        targets = self.extract_targets(target_act)
        for obj in helpers.progressBar(self.objects, prefix = 'Progress:', suffix = 'Complete', length = 50):
            obj.get_closest_distance(targets, target_act)

    def extract_targets(self, target_act):
        """
        Find targets
        """
        targets = []
        for obj in self.objects:
            if target_act in obj.activities:
                targets.append(obj.geom.centroid)
        return MultiPoint(targets)

    def geodataframe(self, single_use=False):
        if single_use:

            df = pd.DataFrame(
                (summary for o in self.objects for summary in o.single_activity_summaries())
            )
            return gp.GeoDataFrame(df, geometry='geometry', crs=self.crs)

        df = pd.DataFrame(
            (o.summary() for o in self.objects)
        )
        return gp.GeoDataFrame(df, geometry='geometry', crs=self.crs)

    # def extract(self):
    #     df = pd.DataFrame.from_records(
    #         ((b.idx, b.geom.centroid) for b in self.objects),
    #         columns=['idx', 'tags', 'geom']
    #     )
    #     return gp.GeoDataFrame(df, geometry='geom')
