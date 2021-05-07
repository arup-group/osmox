# OSM Building Extractor

*Under Construction*

A tool for extracting locations and features from Open Street Map (OSM) data.

## Install

```
git clone git@github.com:arup-group/osmox.git
pip install osmox
# or pip -e install osmox
cd osmox
pytest
osmox --help
```

## Run

`osmox run <CONFIG_PATH> <INPUT_PATH> <OUTPUT_PATH>` is the main entry point for OSMOX:

```{sh}
osmox run --help

Usage: osmox run [OPTIONS] CONFIG_PATH INPUT_PATH OUTPUT_PATH

Options:
  -crs, --crs TEXT  crs string eg (default): 'epsg:27700' (UK grid)
  --help            Show this message and exit.

```

We describe configs below. The `<INPUT_PATH>` should point to an OSM map dataset (for example `osm.pbf`). The `<OUTPUT_PATH>` should point to an output directory.

## Configs

Configs are important. So we provide some examples in `mc/configs` and a validation method:

```{sh}
osmox validate <CONFIG PATH>
```

OSMOX features and associated configurations are described in the various sections below.

## Output

After running `osmox run <CONFIG_PATH> <INPUT_PATH> <OUTPUT_PATH>` you should see something like the following (slowly if you are processing a large map) appear in your terminal:

```{sh}
Loading config from 'configs/config_NTS_UK.json'.
Configured activities: ['education', 'home', 'medical', 'other', 'shop', 'transit', 'visit', 'work']
INFO:osmox.main: Filtering all objects found in data/suffolk-latest.osm.pbf.
INFO:osmox.main: Found 118544 buildings.
INFO:osmox.main: Found 2661 nodes with valid tags.
INFO:osmox.main: Found 5647 areas with valid tags.
INFO:osmox.main: Assigning object tags.
Progress: |██████████████████████████████████████████████████| 100.0% Complete
INFO:osmox.main: Finished assigning tags: f{'existing': 49457, 'points': 711, 'areas': 54422, 'defaults': 13954}.
INFO:osmox.main: Assigning object activities.
Progress: |██████████████████████████████████████████████████| 100.0% Complete
INFO:osmox.main: Assigning object features: ['units', 'levels', 'area', 'floor_area'].
Progress: |██████████████████████████████████████████████████| 100.0% Complete
INFO:osmox.main: Assigning distances to nearest transit.
Progress: |██████████████████████████████████████████████████| 100.0% Complete
INFO:osmox.main: Assigning distances to nearest education.
Progress: |██████████████████████████████████████████████████| 100.0% Complete
INFO:osmox.main: Assigning distances to nearest shop.
Progress: |██████████████████████████████████████████████████| 100.0% Complete
INFO:osmox.main: Assigning distances to nearest medical.
Progress: |██████████████████████████████████████████████████| 100.0% Complete
INFO:osmox.main: Writting objects to: suffolk2/epsg_27700.geojson
INFO:osmox.main: Reprojecting output to epsg:4326 (lat lon)
INFO:osmox.main: Writting objects to: suffolk2/epsg_4326.geojson
INFO:osmox.main:Done.
```

Once complete you will find osmox has created one or two output `.geojson` in the specified `<OUTPUT_PATH>`. If you have specified a crs, you will find your outputs as both this crs and as epsg4326.

We generally refer to the outputs collectively as `facilities` and the properties as `features`. Note that each facility has a unique id, a bunch of features (depending on the configuration) and a point geometry. In the case of areas or polygons, such as buildings, the point represents the centroid. Measured features such as `floor_area` and `distance_to_nearest_X` are measured in the specified crs. Generally we assume you will specify a grid crs such as 27700 for the UK.

```{geojson}
{
    "id": "32653",
    "type": "Feature",
    "properties": {
        "activities": "home",
        "area": 72,
        "distance_to_nearest_education": 298.3127023231315,
        "floor_area": 144.0,
        "id": 717793726,
        "levels": 2.0,
        "distance_to_nearest_medical": 614.1725582520537,
        "distance_to_nearest_shop": 170.41317833861532,
        "distance_to_nearest_transit": 157.88388248911602,
        "units": 1
        }, 
    "geometry": {
        "type": "Point",
        "coordinates": [613632.5100411727, 242323.73560476975]
    }
}
```

## Definitions

**OSMObjects** - objects extracted from OSM. These can be points, lines or polygons. Objects have features.
**OSMFeatures** - OSM objects have features. Features typically include a key and value based on the [OSM wiki](https://wiki.openstreetmap.org/wiki/Map_features).

## Primary Functionality

The primary use case for osmox is for extracting a representation of places where people can do various activities ('education' or 'work' or 'shop' for example). This is done applying a configured mapping to OSM tags:

- **Filter** OSM objects based on OSM tags (eg: select 'building:yes' objects). Filtered objects are defined in a `config.json`. For example, if we were interested in extracting education type `buildings`:

```{json}
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

```{json}
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

## Spatial Inference

Because OSMObjects do not always contain useful tags, we also infer object tags based on spatial operations with surrounding tags. The most common use case for this are building objects that are simply tagged as `building:yes`. We use the below logic to infer useful tags, such as 'building:shop' or 'building:residential'.

- **Contains.** - If an OSMObject has no activity mappable tags (eg `building:yes`), tags are assigned based on the tags of objects that are contained within. For example, a building that contains an `amenity:shop` point is then tagged as `amenity:shop`.
- **Within.** - Where an OSM object *still* does not have a useful OSM tag - tags are assigned based on the tags of objects that contain the object. The most common case is for untagged buildings to be assigned based on landuse objects. For example, a building within a `landuse:residential` area will be assigned with `landuse:residential`.

In both cases we need to add the OSMTags we plan to use to the `activity_mapping` config, eg:

```{json}
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
```

- **Default.** - Where an OSMObject *still* does not have a useful OSM tag, we can optionally apply defaults. Again, these are set in the config:

```{json}
"default_activities": ["home"]
```

## Feature Extraction

Beyond simple assignment of human activities based on OSM tags, we also support the extraction of other features:

- tags (eg 'building:yes')
- floor areas
- units (eg residential units in a building)

These can be configured as follows:

```{json}
"features_config": ["units", "floors", "area", "floor_area"]
```

## Distance to Nearest Extraction

OSMOX also supports calculating distance to nearest features based on object activities. For example we can extract nearest distance to `transit`, `education`, `shop` and `medical` by adding the following to the config:

```{json}
"distance_to_nearest": ["transit", "education", "shop", "medical"],
```

Note that the selected activities are based on the activity mapping config. Any activities should therefore be included in the activity mapping part of the config. You can use `osmox validate <CONFIG PATH>` to check if a config is correctly configured.

## Fill Missing Activities

We have noted that it is not uncommon for some small urban areas to not have building objects, but to have an appropriate landuse area tagged as 'residential'.

We therefore provide a general solution for filling such areas with a grid of objects. This fill method only fills areas that to not have the required activity.

For example, given an area tagged as `landuse:residential` by OSM, that does not contain any object of activity type `home`, the fill method will add a grid of new objects tagged `building:house`. The new objects will also have activity type `home`, size `10 by 10` and be spaced at `25 by 25`:

```{json}
"fill_missing_activities":
    [
        {
            "area_tags": [["landuse", "residential"]],
            "required_acts": ["home"],
            "new_tags": [["building", "house"]],
            "size": [10, 10],
            "spacing": [25, 25]
        }
    ]
```

Multiple groups can be defined:

```{json}
"fill_missing_activities":
    [
        {
            "area_tags": [["landuse", "residential"]],
            "required_acts": ["home"],
            "new_tags": [["building", "house"]],
            "size": [10, 10],
            "spacing": [25, 25]
        },
        {
            "area_tags": [["landuse", "forest"], ["landuse", "orchard"]],
            "required_acts": ["tree_climbing", "glamping"],
            "new_tags": [["amenity", "tree"], ["building", "tree house"]],
            "size": [3, 3],
            "spacing": [8, 8]
        }
    ]
```

Note that the selected activities are based on the activity mapping config. Any activities should therefore be included in the activity mapping part of the config. You can use `osmox validate <CONFIG PATH>` to check if a config is correctly configured.


## TODO

- todo add support to keep original geometries
- add .shp option
- add other distance or similar type features, eg count of nearest neighbours
