
# OSMOX Run

`#!shell osmox run <CONFIG_PATH> <INPUT_PATH> <OUTPUT_NAME>` is the main entry point for OSMOX.
Available options are detailed in on our [Command Line Interface reference page](api/cli.md).

Configuration options are described in a [separate page](config.md).
The `<INPUT_PATH>` should point to an OSM map dataset (`osm.xml` and `osm.pbf` are supported).
The `<OUTPUT_NAME>` should be the desired name of the geopackage output file i.e. `isle-of-man`.

## Using Docker

### Build the image

```shell
docker build -t "osmox" .
```

### Running OSMOX in a container

Once you have built the image, the only thing you need to do is add the path to the folder where your inputs are stored to the command, in order to mount that folder (i.e. give the container access to the data in this folder):

```shell
docker run -v DATA_FOLDER_PATH:/MOUNT_PATH osmox CONFIG_PATH INPUT_PATH OUTPUT_NAME -f geopackage -crs epsg:27700 -l
```

For example, if your input data and config is stored on your machine in `/Users/user_1/mydata`, and this is also the directory where you wish to place the outputs:

```shell
docker run -v /Users/user_1/mydata:/mnt/mydata osmox /mnt/mydata/example_config.json /mnt/mydata/isle-of-man-latest.osm.pbf example/isle-of-man -f geopackage -crs epsg:27700 -l
```

## Options

The most common option you will need to use is `crs`.
The default CRS is British National Grid (BNG, or EPSG:27700), so if you are working outside the UK you should adjust this accordingly.
Specifying a relevant CRS for your data is important if you would like to extract sensible units of measurement for distances and areas.
If this isn't a concern, you can specify CRS as WGS-84 (`-crs epsg:4326`).

OSMOX will return multi-use objects where applicable.
For example, a building that contains both a restaurant and a shop can be labelled with `activities: "eating,shopping"`.
This can make simple mapping of outputs quite complex, as there are many possible combinations of joined use.
To work around this problem, the optional flag `-s` or `--single_use` may be set to instead output unique objects for each activity.
For example, for the above case, extracting two identical buildings, one with `activity: "eating"` and the other with `activity: "shopping"`.

Writing to multiple file formats is supported. The default is geopackage (`.gpkg`), with additional support for GeoJSON (`.geojson`) and geoparquet (`.parquet`).

## Output

After running `osmox run <CONFIG_PATH> <INPUT_PATH> <OUTPUT_NAME>` you should see something like the following (slowly if you are processing a large map) appear in your terminal:

```shell
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
INFO:osmox.main: Writing objects to: suffolk2/suffolk_epsg_27700.gpkg
INFO:osmox.main: Reprojecting output to epsg:4326 (lat lon)
INFO:osmox.main: Writing objects to: suffolk2/suffolk_epsg_4326.gpkg
INFO:osmox.main:Done.
```

Once completed, you will find OSMOX has output file(s) in `geojson` format in the same folder as the OSM input file.
If you have specified a CRS, you will find two output files, named as follows:

1. `<OUTPUT_NAME>_<specified CRS name>.gpkg`
2. `<OUTPUT_NAME>_epsg_4326.gpkg`

We generally refer to the outputs collectively as `facilities` and their properties as `features`.
Note that each facility has a unique id, a number of features (depending on the configuration) and a point geometry.
In the case of areas or polygons, such as buildings, the point represents the centroid.

If we had saved the oputput to GeoJSON - a plain text format - it would look like this on inspection:

```json
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

In the [quick start demo](quick_start.md), we specified the coordinate reference system as `epsg:27700` (this is the default, but we specified it for visibility) so that distance- and area-based features would have sensible units (metres in this case).
If extracting data from other regions, we would encourage using the local CRS.
