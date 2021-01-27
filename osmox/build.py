import json
import pandas as pd
import geopandas as gp
from collections import defaultdict
import osmium
import shapely.wkb as wkblib
import logging
from collections import namedtuple
from pyproj import Proj, Transformer
from shapely.ops import transform


from osmox import config, helpers


OSMTag = namedtuple('OSMtag', 'key value')
OSMObject = namedtuple('OSMobject', 'idx, activity_tags, geom')
AVAILABLE_FEATURES = [
    "area",
    "levels",
    "floor_area",
    "units",
]

class Object:

    DEFAULT_LEVELS = {  # for if a level tag is required but not found
        "apartments": 4,
        "bungalow": 1,
        "detached": 2,
        "dormitory": 4,
        "hotel": 3,
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
            return int(self.osm_tags['building:levels'])  # todo ensure integer
        if 'height' in self.osm_tags:
            height = helpers.height_to_m(self.osm_tags['height'])
            if height:
                return int(height / 4)
        if self.osm_tags["building"] in self.DEFAULT_LEVELS:
            return self.DEFAULT_LEVELS[self.osm_tags["building"]]
        return 2

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

    def summary(self):
        fixed = {
            "id": self.idx,
            "activities": ','.join(self.activities),
            "geometry": self.geom.centroid
        }
        return {**fixed, **self.features}


class ObjectHandler(osmium.SimpleHandler):

    wkbfab = osmium.geom.WKBFactory()
    logger = logging.getLogger(__name__)

    def __init__(self, config, crs='epsg:27700', from_crs='epsg:4326', level=logging.DEBUG):

        super().__init__()
        logging.basicConfig(level=level)
        self.cnfg = config
        self.filter = self.cnfg["filter"]
        self.features_config = self.cnfg["features_config"]
        self.default_activities = self.cnfg["default_activities"]
        self.activity_config = self.cnfg["activity_config"]
        self.transformer = Transformer.from_proj(Proj(from_crs), Proj(crs))

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
    (i) add them to self.found if they are within the filter_config
    (ii) else, add them to self.areas or self.points if they are within the activity_mapping
    """

    def selected(self, tags):
        if tags:
            tags = dict(tags)
            return helpers.dict_list_match(tags, self.filter)

    def get_activity_tags(self, tags):
        """
        Return configured activity tags for an OSM object as list of OSMtags.
        """
        if tags:
            tags = dict(tags)
            found = []
            for osm_key, osm_val in tags.items():
                if osm_key in self.activity_config and osm_val in self.activity_config[osm_key]:
                    found.append(OSMTag(key=osm_key, value=osm_val))
            return found

    def add_object(self, idx, activity_tags, osm_tags, geom):
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
        activity_tags = self.get_activity_tags(n.tags)
        if self.selected(n.tags):
            self.add_object(idx=n.id, osm_tags=n.tags, activity_tags=activity_tags, geom=self.fab_point(n))
        elif activity_tags:
            self.add_point(idx=n.id, activity_tags=activity_tags, geom=self.fab_point(n))

    def area(self, a):
        activity_tags = self.get_activity_tags(a.tags)
        if self.selected(a.tags):
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
            
            if self.default_activities:
                # otherwise apply defaults if set
                self.log["defaults"] += 1
                for a in self.default_activities:
                    obj.apply_default_tag(a)

    def assign_activities(self):
        for obj in helpers.progressBar(self.objects, prefix = 'Progress:', suffix = 'Complete', length = 50):
            obj.assign_activities(self.activity_config)

    def add_features(self):
        """
        ["units", "floors", "area", "floor_area"]
        """
        for obj in helpers.progressBar(self.objects, prefix = 'Progress:', suffix = 'Complete', length = 50):
            obj.add_features(self.features_config)
    
    def dataframe(self):
        df = pd.DataFrame(
            (b.summary() for b in self.objects)
        )
        return gp.GeoDataFrame(df, geometry='geometry')
        
    # def extract(self):
    #     df = pd.DataFrame.from_records(
    #         ((b.idx, b.geom.centroid) for b in self.objects),
    #         columns=['idx', 'tags', 'geom']
    #     )
    #     return gp.GeoDataFrame(df, geometry='geom')
