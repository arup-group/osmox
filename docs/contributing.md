# Contributing

osmox is an actively maintained and utilised project.

## How to contribute

to report issues, request features, or exchange with our community, just follow the links below.

__Is something not working?__

[:material-bug: Report a bug](https://github.com/arup-group/osmox/issues/new?template=BUG-REPORT.yml "Report a bug in osmox by creating an issue and a reproduction"){ .md-button }

__Missing information in our docs?__

[:material-file-document: Report a docs issue](https://github.com/arup-group/osmox/issues/new?template=DOCS.yml "Report missing information or potential inconsistencies in our documentation"){ .md-button }

__Want to submit an idea?__

[:material-lightbulb-on: Request a change](https://github.com/arup-group/osmox/issues/new?template=FEATURE-REQUEST.yml "Propose a change or feature request or suggest an improvement"){ .md-button }

__Have a question or need help?__

[:material-chat-question: Ask a question](https://github.com/arup-group/osmox/discussions "Ask questions on our discussion board and get in touch with our community"){ .md-button }

## Developing osmox

To find beginner-friendly existing bugs and feature requests you may like to start out with, take a look at our [good first issues](https://github.com/arup-group/osmox/contribute).

## Known issues

- OSMOX is slow - for national scale extractions we're talking many hours.
There are some areas that can be sped up, some that will parallelize ok.
But treating all this as premature until an output format is nailed down and there are a few more users.
- We need tests for the use of all `*` in the config filter and mappings.
- We want to move to yaml configs.
- add zonal labelling (eg lsoa assignment).
- perhaps add a sampling format (zone:act:{viables}).
- Add support to keep original geometries.
- add .shp option.
- add other distance or similar type features, eg count of nearest neighbours.
- warning or feedback when trying to process really large datasets.

### Setting up a development environment

To create a development environment for osmox, with all libraries required for development and quality assurance installed, it is easiest to install osmox using the [mamba](https://mamba.readthedocs.io/en/latest/index.html) package manager, as follows:

1. Install mamba with the [Mambaforge](https://github.com/conda-forge/miniforge#mambaforge) executable for your operating system.
1. Open the command line (or the "miniforge prompt" in Windows).
1. Download (a.k.a., clone) the osmox repository: `git clone git@github.com:arup-group/osmox.git`
1. Change into the `osmox` directory: `cd osmox`
1. Create the osmox mamba environment: `mamba create -n osmox -c conda-forge -c city-modelling-lab --file requirements/base.txt --file requirements/dev.txt`
1. Activate the osmox mamba environment: `mamba activate osmox`
1. Install the osmox package into the environment, in editable mode and ignoring dependencies (we have dealt with those when creating the mamba environment): `pip install --no-deps -e .`

All together:

--8<-- "README.md:docs-install-dev"

If installing directly with pip, you can install these libraries using the `dev` option, i.e., `pip install -e '.[dev]'`

If you plan to make changes to the code then please make regular use of the following tools to verify the codebase while you work:

- `pre-commit`: run `pre-commit install` in your command line to load inbuilt checks that will run every time you commit your changes.
  The checks are: 1. check no large files have been staged, 2. lint python files for major errors, 3. format python files to conform with the [PEP8 standard](https://peps.python.org/pep-0008/).
  You can also run these checks yourself at any time to ensure staged changes are clean by calling `pre-commit`.
- `pytest` - run the unit test suite and check test coverage.



### Rapid-fire testing

The following options allow you to strip down the test suite to the bare essentials:


1. You can avoid generating coverage reports, by adding the `--no-cov` argument: `pytest --no-cov`.

### Memory profiling

!!! note
    When you open a pull request (PR), one of the GitHub actions will run memory profiling for you.
    This means you don't *have- to do any profiling locally.
    However, if you can, it is still good practice to do so as you will catch issues earlier.

osmox can be memory intensive; we like to ensure that any development to the core code does not exacerbate this.
If you are running on a UNIX device (i.e., **not*- on Windows), you can test whether any changes you have made adversely impact memory and time performance as follows:

1. Install [memray](https://bloomberg.github.io/memray/index.html) in your `osmox` conda environment: `conda install memray pytest-memray`.
1. Run the memory profiling integration test: `pytest -p memray -m "high_mem" --no-cov`.
1. Optionally, to visualise the memory allocation, run `pytest -p memray -m "high_mem" --no-cov --memray-bin-path=[my_path] --memray-bin-prefix=[my_prefix]` - where you must define `[my_path]` and `[my_prefix]` - followed by `memray flamegraph [my_path]/[my_prefix]-tests-test_100_memory_profiling.py-test_mem.bin`.
   You will then find the HTML report at `[my_path]/memray-flamegraph-[my_prefix]-tests-test_100_memory_profiling.py-test_mem.html`.

All together:

``` shell
conda install memray pytest-memray
pytest -p memray -m "high_mem" --no-cov --memray-bin-path=[my_path] --memray-bin-prefix=[my_prefix]
memray flamegraph [my_path]/[my_prefix]-tests-test_100_memory_profiling.py-test_mem.bin
```

For more information on using memray, refer to their [documentation](https://bloomberg.github.io/memray/index.html).

## Documentation

With any contribution, you may need to update / add to the documentation (in the `docs` directory).
We use [MkDocs](https://www.mkdocs.org/) and the [Material](https://squidfunk.github.io/mkdocs-material/) theme to build and render our documentation, meaning you can write your documentation in Markdown files.

Here are some use-cases that you may come across in which you are considering updating the documentation:

??? question "I have updated the README.md"

    We pipe sections of the README over to the documentation automatically.
    If you put your changes between the commented lines `:::md <!--- --8<-- [start:docs] -->` and `:::md <!--- --8<-- [end:docs] -->` it will find its way to the documentation homepage.

??? question annotate "I want to add a new page"

    Add a Markdown file to the top-level in `docs`, e.g. `docs/my-page.md`.
    Then, add a reference to that file within the `nav` key in `mkdocs.yml`, e.g.:

    ```yaml
    nav:
    - Home: index.md
    - Installation: installation.md
    - Getting started: getting_started.md
    - My Page: my-page.md
    ```

    You can also just rely on your document header to define the name in the navigation:
    `my-page.md`

    ```md
    # My Page
    ...
    ```

    `mkdocs.yml`

    ```yaml
    nav:
    ...
    - my-page.md
    ...
    ```

??? question "I have a new example notebook"

    If the project is set up to include process examples (see `.cruft.json` option `create_jupyter_notebook_directory`),
    then you can just add a [Jupyter notebook](https://jupyter.org/) to the `examples` directory and it will automatically render in the documentation under `Examples`.

??? question "I want to add images to my docs"

    You should add any new images, whether you reference them in a Markdown page or in an example notebook, to the `resources/` directory.
    Within your Markdown, you will be able to reference these as follows:

    ``` html
    <figure>
    <img src="../resources/filename.png", width="100%", style="background-color:white;", alt="accessible alternative text">
    <figcaption>My caption.</figcaption>
    </figure>
    ```

    Or:

    ``` md
    ![accessible alternative text](../resources/filename.png)
    ```

    The first approach gives you a bit more power, including having a figure caption.

??? question "I want to update the CLI/Python API docs"

    As with example notebooks, we update these pages automatically.
    So, if you've added content within your project (a new script, a new CLI function), you will see them in your next iteration of the documentation.

??? question "I want to automatically process a number of files into pages in the docs"

    You may have configuration files you want to add to the documentation for reference.
    You should add your workflow to process these files to `docs/hooks.py`.
    In that file, you can find examples of how we do it for other files (e.g. the python API and the example notebooks).

??? question "I want to view my documentation changes locally"

    You can serve your documentation locally by calling `mkdocs serve` from the command line with [your development environment](#setting-up-a-development-environment) activated.
    Once the documentation has been built you will see a link to navigate to in your browser, most likely <http://127.0.0.1:8000>.
    When you make changes to your documentation, `mkdocs` will automatically rebuild everything so that you can check the effects of your changes without needing to rerun `mkdocs serve`.

??? question "I want to do something else"

    We recommend exploring the [MkDocs](https://www.mkdocs.org/) and the [Material](https://squidfunk.github.io/mkdocs-material/) documentation if we haven't answered your question.

## Updating the project when the template updates

This project has been built with [cruft](https://cruft.github.io/cruft/) based on the [Arup Cookiecutter template](https://github.com/arup-group/cookiecutter-pypackage).
When changes are made to the base template, they can be merged into this project by running `cruft update` from the  `osmox` conda environment.

You may be prompted to do this when you open a Pull Request, if our automated checks identify that the template is newer than that used in the project.

## Submitting changes

--8<-- "CONTRIBUTING.md:docs"
