import logging
import os
import traceback
from pathlib import Path

import pytest
from click.testing import CliRunner
from osmox import cli

logging.basicConfig(level=logging.INFO)

MAP_EXTENSIONS = {"geopackage": ".gpkg", "geojson": ".geojson", "geoparquet": ".parquet"}


@pytest.fixture
def fixtures_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures"))


@pytest.fixture
def config_path(fixtures_root):
    return os.path.join(fixtures_root, "test_config.json")


@pytest.fixture
def toy_osm_path(fixtures_root):
    return os.path.join(fixtures_root, "toy.osm")


@pytest.fixture
def path_output_dir(tmp_path):
    return os.path.join(tmp_path, "output_test")


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def default_output_file_ending():
    return "_epsg_4326.gpkg"


@pytest.fixture
def default_output_file_path(path_output_dir, default_output_file_ending):
    return Path(path_output_dir + default_output_file_ending)


def check_exit_code(result):
    "Print full traceback if the CLI runner failed"
    if result.exit_code != 0:
        traceback.print_tb(result.exc_info[-1])
    assert result.exit_code == 0


def test_cli_with_default_args(
    runner, config_path, toy_osm_path, path_output_dir, default_output_file_path
):
    # Test the command with minimal arguments
    result = runner.invoke(cli.run, [config_path, toy_osm_path, path_output_dir])

    check_exit_code(result)
    assert default_output_file_path.exists()


@pytest.mark.parametrize("output_format", ["geojson", "geopackage", "geoparquet"])
def test_cli_output_formats(
    runner, config_path, toy_osm_path, path_output_dir, default_output_file_path, output_format
):
    result = runner.invoke(
        cli.run,
        [config_path, toy_osm_path, path_output_dir, "-f", output_format, "-crs", "epsg:4326"],
    )
    check_exit_code(result)

    assert default_output_file_path.with_suffix(MAP_EXTENSIONS[output_format]).exists()


@pytest.mark.parametrize("crs", ["epsg:27700"])
def test_cli_output_crs(
    runner, config_path, toy_osm_path, path_output_dir, crs, default_output_file_path
):
    result = runner.invoke(cli.run, [config_path, toy_osm_path, path_output_dir, "-crs", crs])
    check_exit_code(result)

    # test that file with default crs is still produced
    assert default_output_file_path.exists()

    out_path = Path(path_output_dir + "_epsg_27700.gpkg")
    assert out_path.exists()
