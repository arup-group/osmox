# OSM Ox

A tool for extracting locations and features from Open Street Map (OSM) data.

## Why?

We use Osmox to extract locations from OSM for city or national scale agent based models. This tends to focus on extracting buildings and their likelly usages, for example `homes`, `schools`, `medical facilities` and `places of work`. But can also be abstracted to other objects such as transit, parks or land use.

Under the hood Osmox is a collection of labelling and GIS type operations:

- filtering
- activity labelling
- simple spatial activity inference
- feature extraction (such as floor areas)
- filling missing data

 Assembled togther they form part of our wider pipeline. But as a standalone tool, Osmox is useful for extracting insights from OSM in a reproducible manner.

 ![isle of man distance_to_nearest_transit](./readme_fixtures/distance-to-transit.png)
*^ Isle of Man `distance_to_nearest_transit`.*

## Install

```{sh}
git clone git@github.com:arup-group/osmox.git
pip install osmox
# or pip -e install osmox
cd osmox
pytest
osmox --help
```

## Quick Start

Extract `home`, `work`, `education`, `shop` and various other activity locations ("facilities") for the Isle of Man:

`osmox run configs/example.json example_data/isle-of-man.osm example -crs "epsg:27700"` (paths given from osmox project root)

After about 30 seconds you should find locations for the extract facilities in the specified `example` directory. Each facility includes a number of facilities as per the config:

```{geojson}
{
    "type": "FeatureCollection",
    "features": [
        ...
        {
        "id": "13589",
        "type": "Feature",
        "properties": {
            "activities": "home",
            "area": 196,
            "distance_to_nearest_education": 816.4434678355371,
            "distance_to_nearest_medical": 366.81198701080626,
            "distance_to_nearest_shop": 133.12877450643526,
            "distance_to_nearest_transit": 122.33125535187033,
            "floor_area": 392.0,
            "id": 1869954720,
            "levels": 2.0,
            "units": 1
            },
        "geometry": {
            "type": "Point",
            "coordinates": [220894.60596542264, 467332.85704661923]
            }
        },
        ...
```

Outputs are written as WGS 84 (epsg:4326), so that they can be quickly inspected via [kepler](https://kepler.gl) or equivalent:

![isle of man floor areas](./readme_fixtures/floor-areas.png)
*^ Isle of Man facility `floor_area` feature. Approximated based on polygon areas and floor labels or sensible defaults.*

![isle of man activites](./readme_fixtures/activities.png)
*^ Isle of Man `activities` feature. For simulations we use this information to control what agents can do where, but this is also a good disagregate proxy for land-use. In this example, blue areas are residential, orange commercial and brown is other work places.*

## Osmox Run

`osmox run <CONFIG_PATH> <INPUT_PATH> <OUTPUT_PATH>` is the main entry point for OSMOX:

```{sh}
osmox run --help

Usage: osmox run [OPTIONS] CONFIG_PATH INPUT_PATH OUTPUT_PATH

Options:
  -crs, --crs TEXT  crs string eg (default): 'epsg:27700' (UK grid)
  --help            Show this message and exit.

```

We describe configs below. The `<INPUT_PATH>` should point to an OSM map dataset (`osm`(xml) and `osm.pbf` are supported). The `<OUTPUT_PATH>` should point to an exiting or new output directory.

## Configs

Configs are important. So we provide some examples in `mc/configs` and a validation method for when you start editing or building your own configs:

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

We generally refer to the outputs collectively as `facilities` and the properties as `features`. Note that each facility has a unique id, a bunch of features (depending on the configuration) and a point geometry. In the case of areas or polygons, such as buildings, the point represents the centroid.

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

In the quick start demo, we specified the coordinate reference system as `epsg:27700` (this is the default, but we specified it for visibility) so that distance and area based features would have sensible units (metres in this case). If extracting data from other areas we would encourage using the relevant grid crs for that area.

## Configuration

### Definitions

**OSMObjects** - objects extracted from OSM. These can be points, lines or polygons. Objects have features.
**OSMFeatures** - OSM objects have features. Features typically include a key and value based on the [OSM wiki](https://wiki.openstreetmap.org/wiki/Map_features).

### Primary Functionality

The primary use case for osmox is for extracting a representation of places where people can do various activities ('education' or 'work' or 'shop' for example). This is done applying a configured mapping to OSM tags:

- **Filter** OSM objects based on OSM tags (eg: select 'building:yes' objects). Filtered objects are defined in a `config.json`. For example, if we were interested in extracting education type `buildings`:

```{json}
{
    "filter": {
        "building": [
            "kindergarden",
            "school",
            "university",
            "college",
            "yes"
        ]
    }, ...
}
```

- **Activity Map** object activities based on OSM tags (eg: this building type 'university' is an education facility). Activity mapping is based on the same `config.json`, but we add a new section `activity_mapping`. For each OSMTag (a key such as `building` and a value such as `hotel`,) we map a list of activities:

```{json}
{
    ...
    "activity_mapping": {
        "building": {
            "hotel": ["work", "visit"],
            "residential": ["home"]
        }
    }
}
```

Because an OSM tag key is often sufficient to make an activity mapping, we allow use of `*` as "all":

```{json}
{
    ...
    "activity_mapping": {
      ...
        "office": {
            "*": ["work"]
        }
    }
}
```

Note that the filter controls the final objects that get extracted but that the activity mapping is more general. It is typical to map tags that are not included in the filter because these can be used by subsequent steps (such as inference) to assign activities where otherwise useful tags aren't included. There is no harm in over specifying the mapping.

These configs get looong - but we've supplied some full examples in the project.

### Spatial Inference

Because OSMObjects do not always contain useful tags, we also infer object tags based on spatial operations with surrounding tags.

The most common use case for this is building objects that are simply tagged as `building:yes`. We use the below logic to infer useful tags, such as 'building:shop' or 'building:residential'.

- **Contains.** - If an OSMObject has no mappable tags (eg `building:yes`), tags are assigned based on the tags of objects that are contained within. For example, a building that contains an `amenity:shop` point is then tagged as `amenity:shop`.
- **Within.** - Where an OSM object *still* does not have a useful OSM tag - tags are assigned based on the tags of objects that contain the object. The most common case is for untagged buildings to be assigned based on landuse objects. For example, a building within a `landuse:residential` area will be assigned with `landuse:residential`.

In both cases we need to add the OSMTags we plan to use to the `activity_mapping` config, eg:

```{json}
{
    ....
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
{
    ...
    "default_tags": [["building", "residential"]],
    ...
}
```

### Feature Extraction

Beyond simple assignment of human activities based on OSM tags, we also support the extraction of other features:

- areas
- floors
- floor areas
- units (eg residential units in a building)

These can be configured as follows:

```{json}
{
    ...
    "features_config": ["units", "floors", "area", "floor_area"]
    ...
}
```

### Distance to Nearest Extraction

OSMOX also supports calculating distance to nearest features based on object activities. For example we can extract nearest distance to `transit`, `education`, `shop` and `medical` by adding the following to the config:

```{json}
{
    ...
    "distance_to_nearest": ["transit", "education", "shop", "medical"],
    ...
}
```

Note that the selected activities are based on the activity mapping config. Any activities should therefore be included in the activity mapping part of the config. You can use `osmox validate <CONFIG PATH>` to check if a config is correctly configured.

### Fill Missing Activities

We have noted that it is not uncommon for some small areas to not have building objects, but to have an appropriate landuse area tagged as 'residential'.

We therefore provide a very ad-hoc solution for filling such areas with a grid of objects. This fill method only fills areas that do not have the required activities already within them.

For example, given an area tagged as `landuse:residential` by OSM, that does not contain any object of activity type `home`, the fill method will add a grid of new objects tagged `building:house`. The new objects will also have activity type `home`, size `10 by 10` and be spaced at `25 by 25`:

```{json}
{
    ...
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
}
```

![isle of man distance_to_nearest_transit](./readme_fixtures/activity-fill.png)
*^ Example Isle of Man activity filling in action for a residential area without building locations.*

Note that the selected activities are based on the activity mapping config. Any activities should therefore be included in the activity mapping part of the config. You can use `osmox validate <CONFIG PATH>` to check if a config is correctly configured.

Multiple groups can also be defined, for example:

```{json}
{
    ...
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
    ....
}
```

## TODO

- this is slow for sure - for national scale extractions we're talking many hours. There are some areas that can be sped up, some that will paralellize ok. But treating all this as premature until an output format is nailed down and there are a few more users
- move to toml/yaml configs (but maybe not the json is ok)
- add zonal labelling (eg lsoa assignment)
- perhaps add a sampling format (zone:act:{viables})
- todo add support to keep original geometries
- add .shp option
- add other distance or similar type features, eg count of nearest neighbours
- warning or feedback when trying to process really large datasets
