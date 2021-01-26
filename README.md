# OSM Building Extractor

*Under Construction*

A tool for extracting locations and features from Open Street Map (OSM) data.

## Install

```
git clone https://github.com/fredshone/osmbx
pip install osmbx
osmox pytest
osmox --help
```

## Run

```
osmox validate <CONFIG PATH>
osmox run <CONFIG PATH> <INPUT OSM/OSM.PBF PATH> <OUTPUT PATH>
```

## Output

WIP

[
    id: {
        act: ,
        building: ,
        osm: ,
        area: ,
        floors: ,
    }
]

## Definitions

**OSMObjects** - objects extracted from OSM. These can be points, lines or polygons. Objects have features.
**OSMFeatures** - OSM objects have features. Features typically include a key and value based on the [OSM wiki](https://wiki.openstreetmap.org/wiki/Map_features).

## Primary Functionality

The primary use case for OSMBX is for extracting a representation of places where people can do various activities ('education' or 'work' or 'shop' for example). This is done applying a configured mapping to OSM tags:

- **Filter** OSM objects based on OSM tags (eg: select 'building:yes' objects). Filtered objects are defined in a `config.json`. For example, if we were interested in extracting education type `buildings`:
```
{
    "filter": {
        "building": [
            "kindergarden",
            "school",
            "university",
            "college"
        ]
    }
}
```
- **Activity Map** object activities based on OSM tags (eg: this building type 'university' is an education facility). Activity mapping is based on the same `config.json`, but we add a new section `activity_mapping`. For each OSMTag (a key such as `building` and a value such as `hotel`,) we map a list of activities:
```
{
  "activity_mapping": {
        "building": {
            "hotel": ["work", "visit"],
            "residential": ["home"]
        }
    }
}
```
These configs get looong - but we've supplied some full examples in the project.

## Spatial Inference:

Because OSMObjects to not always contain useful tags, we also infer object tags based on spatial operations with surrounding tags. The most common use case for this are building objects that are simply tagged as `building:yes`. We use the below logic to infer useful tags, such as 'building:shop' or 'building:residential'.

- **Contains.** - If an OSMObject has no activity mappable tags (eg `building:yes`), tags are assigned based on the tags of objects that are contained within. For example, a building that contains an `amenity:shop` point is then tagged as `amenity:shop`.
- **Within.** - Where an OSM object *still* does not have a useful OSM tag - tags are assigned based on the tags of objects that contain the object. The most common case is for untagged buildings to be assigned based on landuse objects. For example, a building within a `landuse:residential` area will be assigned with `landuse:residential`.

In both cases we need to add the OSMTags we plan to use to the `activity_mapping` config, eg:
{
  "activity_mapping": {
        "building": {
            "hotel": ["work", "visit"],
            "residential": ["home"]
        },
        "amenity": {
          "cafe": ["work", "eat"]
        },
        "landuse": {
          "residential": ["home"]
        }
    }
}

- **Default.** - Where an OSMObject *still* does not have a useful OSM tag, we can optionally apply defaults. Again, these are set in the config:
```
"default_activities": ["home"]
```

## Feature Extraction:

Beyond simple assignment of human activities based on OSM tags, we also support the extraction of other features:

- tags (eg 'building:yes')
- floor areas
- units (eg residential units in a building)

These can be configured as follows:

```
"features_config": ["units", "floors", "area", "floor_area"]
```

The intention is to extend these features to include spatial fatures, such as distance to public transit.
