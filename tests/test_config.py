import os

import jsonschema
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


@pytest.fixture
def strict_schema_validator():
    strict = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://json-schema.org/draft/2020-12/strict",
        "$ref": "https://json-schema.org/draft/2020-12/schema",
        "unevaluatedProperties": False,
    }
    return jsonschema.Draft202012Validator(strict)


def test_schema(strict_schema_validator):
    strict_schema_validator.check_schema(config.SCHEMA)


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


def test_config_with_missing_filter_logging(valid_config):
    valid_config.pop("filter")
    with pytest.raises(
        jsonschema.exceptions.ValidationError, match="'filter' is a required property"
    ):
        config.validate_activity_config(valid_config)


def test_config_with_missing_activity_mapping_logging(valid_config):
    valid_config.pop("activity_mapping")

    with pytest.raises(
        jsonschema.exceptions.ValidationError, match="'activity_mapping' is a required property"
    ):
        config.validate_activity_config(valid_config)


def test_config_with_unsupported_object_features_logging(valid_config):
    valid_config["object_features"].append("invalid_feature")
    with pytest.raises(
        jsonschema.exceptions.ValidationError, match="'invalid_feature' is not one of"
    ):
        config.validate_activity_config(valid_config)


def test_config_with_unsupported_distance_to_nearest_activity_logging(valid_config):
    valid_config["distance_to_nearest"].append("invalid_activity")
    with pytest.raises(
        ValueError,
        match="'Distance to nearest' has non-configured activities: {'invalid_activity'}",
    ):
        config.validate_activity_config(valid_config)


def test_config_with_missing_fill_missing_activities_key_logging(valid_config):
    valid_config["fill_missing_activities"][0].pop("required_acts")
    with pytest.raises(
        jsonschema.exceptions.ValidationError, match="'required_acts' is a required property"
    ):
        config.validate_activity_config(valid_config)


def test_config_with_invalid_activity_for_fill_missing_activities_logging(valid_config):
    valid_config["fill_missing_activities"][0]["required_acts"].append("invalid_activity")
    with pytest.raises(
        ValueError,
        match="'Fill missing activities' group has non-configured activities: {'invalid_activity'}",
    ):
        config.validate_activity_config(valid_config)
