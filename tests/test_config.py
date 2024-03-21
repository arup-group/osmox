import os

import pytest
from osmox import config

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures"))
test_config_path = os.path.join(root, "test_config.json")


@pytest.fixture
def valid_config():
    return {
        "filter": {
            "building": ["house", "yes"],
            "public_transport": ["*"],
            "highway": ["bus_stop"],
        },
        "object_features": ["units", "levels", "area", "floor_area"],
        "distance_to_nearest": ["transit", "shop"],
        "default_tags": [["building", "house"]],
        "activity_mapping": {
            "building": {"house": ["home"]},
            "amenity": {
                "pub": ["social", "work", "delivery"],
                "fast_food": ["work", "delivery", "food_shop"],
            },
            "landuse": {"commercial": ["shop", "work", "delivery"], "residential": ["home"]},
            "shop": {"*": ["shop", "work"]},
            "public_transport": {"*": ["transit"]},
            "highway": {"bus_stop": ["transit"]},
        },
        "fill_missing_activities": [
            {
                "area_tags": [["landuse", "residential"]],
                "required_acts": ["home"],
                "new_tags": [["building", "house"]],
                "size": [10, 10],
                "spacing": [25, 25],
            }
        ],
    }


def test_load_config():
    cnfg = config.load(test_config_path)
    assert cnfg
    assert isinstance(cnfg, dict)


def test_get_acts(valid_config):
    assert config.get_acts(valid_config) == {
        "home",
        "shop",
        "social",
        "work",
        "delivery",
        "food_shop",
        "transit",
    }


def test_get_tags(valid_config):
    assert config.get_tags(valid_config) == (
        {"building", "public_transport", "highway"},
        {
            ("building", "house"),
            ("building", "yes"),
            ("public_transport", "*"),
            ("highway", "bus_stop"),
        },
    )


def test_valid_config_logging(caplog, valid_config):
    config.validate_activity_config(valid_config)
    assert "['delivery', 'food_shop', 'home', 'shop', 'social', 'transit', 'work']" in caplog.text


def test_config_with_missing_filter_logging(caplog, valid_config):
    valid_config.pop("filter")
    config.validate_activity_config(valid_config)
    assert "No 'filter' found in config." in caplog.text


def test_config_with_missing_activity_mapping_logging(caplog, valid_config):
    valid_config.pop("activity_mapping")
    config.validate_activity_config(valid_config)
    assert "No 'activity_config' found in config." in caplog.text


def test_config_with_unsupported_object_features_logging(caplog, valid_config):
    valid_config["object_features"].append("invalid_feature")
    config.validate_activity_config(valid_config)
    assert "Unsupported features in config: {'invalid_feature'}," in caplog.text


def test_config_with_unsupported_distance_to_nearest_activity_logging(caplog, valid_config):
    valid_config["distance_to_nearest"].append("invalid_activity")
    config.validate_activity_config(valid_config)
    assert "'Distance to nearest' has a non-configured activity 'invalid_activity'" in caplog.text


def test_config_with_missing_fill_missing_activities_key_logging(caplog, valid_config):
    valid_config["fill_missing_activities"][0].pop("required_acts")
    config.validate_activity_config(valid_config)
    assert "'Fill missing activities' group is missing required key: required_acts" in caplog.text


def test_config_with_invalid_activity_for_fill_missing_activities_logging(caplog, valid_config):
    valid_config["fill_missing_activities"][0]["required_acts"].append("invalid_activity")
    config.validate_activity_config(valid_config)
    assert (
        "'Fill missing activities' group has a non-configured activity 'invalid_activity'"
        in caplog.text
    )
