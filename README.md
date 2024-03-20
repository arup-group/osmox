<!--- the "--8<--" html comments define what part of the README to add to the index page of the documentation -->
<!--- --8<-- [start:docs] -->
# OSMOX

A tool for extracting locations and features from OpenStreetMap (OSM) data.

## Why?

We use OSMOX to extract locations from OSM for city or national scale agent-based models. In particular, the focus tends to be on extracting buildings and their designated usages, for example `homes`, `schools`, `medical facilities` and `places of work`. However, this can also be abstracted to other objects such as transit, parks or land use.

Under the hood, OSMOX is a collection of labelling and GIS-type operations:

- filtering
- activity labelling
- simple spatial activity inference
- feature extraction (such as floor areas)
- filling in missing data

Once assembled, these form part of our wider pipeline. But as a standalone tool, OSMOX is useful for extracting insights from OSM in a reproducible manner.

![isle of man distance_to_nearest_transit](resources/distance-to-transit.png)
*^ Isle of Man `distance_to_nearest_transit`.*

<!--- --8<-- [end:docs] -->

## Documentation

For more detailed instructions, see our [documentation](https://arup-group.github.io/osmox/latest).

## Installation

OSMOX can be installed in Python environments from version 3.10 upwards.

Note: you can use the instructions [here](#as-a-user-docker-image) to build a Docker image for OSMOX and run it in a container if you cannot install it locally.
This builds in a Python 3.12 environment.

### As a user (Docker image)

```shell
git clone git@github.com:arup-group/osmox.git
cd osmox
docker build -t "osmox" .
```

### As a user (Python package)

To install osmox, we recommend using the [mamba](https://mamba.readthedocs.io/en/latest/index.html) package manager:

<!--- --8<-- [start:docs-install-user] -->
``` shell
git clone git@github.com:arup-group/osmox.git
cd osmox
mamba create -n osmox -c conda-forge -c city-modelling-lab --file requirements/base.txt
mamba activate osmox
pip install --no-deps .
```
<!--- --8<-- [end:docs-install-user] -->

### As a developer

<!--- --8<-- [start:docs-install-dev] -->
``` shell
git clone git@github.com:arup-group/osmox.git
cd osmox
mamba create -n osmox -c conda-forge -c city-modelling-lab --file requirements/base.txt --file requirements/dev.txt
mamba activate osmox
pip install --no-deps -e .
```
<!--- --8<-- [end:docs-install-dev] -->

For more detailed instructions, see our [documentation](https://arup-group.github.io/osmox/latest/installation/).

## Contributing

There are many ways to contribute to osmox.
Before making contributions to the osmox source code, see our contribution guidelines and follow the [development install instructions](#as-a-developer).

If you plan to make changes to the code then please make regular use of the following tools to verify the codebase while you work:

- `pre-commit`: run `pre-commit install` in your command line to load inbuilt checks that will run every time you commit your changes.
The checks are: 1. check no large files have been staged, 2. lint python files for major errors, 3. format python files to conform with the [pep8 standard](https://peps.python.org/pep-0008/).
You can also run these checks yourself at any time to ensure staged changes are clean by simple calling `pre-commit`.
- `pytest` - run the unit test suite and check test coverage.
- `pytest -p memray -m "high_mem" --no-cov` (not available on Windows) - after installing memray (`mamba install memray pytest-memray`), test that memory and time performance does not exceed benchmarks.

For more information, see our [documentation](https://arup-group.github.io/osmox/latest/contributing/).

## Building the documentation

If you are unable to access the online documentation, you can build the documentation locally.
First, [install a development environment of osmox](https://arup-group.github.io/osmox/latest/contributing/coding/), then deploy the documentation using [mike](https://github.com/jimporter/mike):

```
mike deploy develop
mike serve
```

Then you can view the documentation in a browser at http://localhost:8000/.
