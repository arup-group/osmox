import logging
import os
import traceback

import pytest
from click.testing import CliRunner
from osmox import cli

logging.basicConfig(level=logging.INFO)


@pytest.fixture
def fixtures_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures"))


@pytest.fixture
def config_path(fixtures_root):
    return os.path.join(fixtures_root, "test_config.json")


@pytest.fixture
def toy_osm_path(fixtures_root):
    return os.path.join(fixtures_root, "park.osm")


@pytest.fixture
def runner():
    return CliRunner()


def check_exit_code(result):
    "Print full traceback if the CLI runner failed"
    if result.exit_code != 0:
        traceback.print_tb(result.exc_info[-1])
    assert result.exit_code == 0


def test_cli_with_default_args(runner, config_path, toy_osm_path):
    # Test the command with minimal arguments
    result = runner.invoke(cli.run, [config_path, toy_osm_path, "output_test"])

    check_exit_code(result)
    assert "geopackage" in result.exit_code
    assert "epsg:4326" in result.exit_code


def test_cli_output_formats(runner, config_path, toy_osm_path):
    for output_format in ["geojson", "geopackage", "geoparquet"]:
        result = runner.invoke(
            cli.run,
            [config_path, toy_osm_path, "output_test", "-f", output_format, "-crs", "epsg:4326"],
        )
        check_exit_code(result)
