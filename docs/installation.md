
# Installation

## Setting up a user environment

As a `osmox` user, it is easiest to install using the [mamba](https://mamba.readthedocs.io/en/latest/index.html) package manager, as follows:

1. Install mamba with the [Mambaforge](https://github.com/conda-forge/miniforge#mambaforge) executable for your operating system.
1. Open the command line (or the "miniforge prompt" in Windows).
1. Create the osmox mamba environment: `mamba create -n osmox -c conda-forge -c city-modelling-lab osmox`
1. Activate the osmox mamba environment: `mamba activate osmox`

All together:

--8<-- "README.md:docs-install-user"

## Setting up a development environment

The install instructions are slightly different to create a development environment compared to a user environment:

--8<-- "README.md:docs-install-dev"

For more detailed installation instructions specific to developing the osmox codebase, see our [development documentation][setting-up-a-development-environment].
