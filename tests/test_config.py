import os
import pytest
from collections import defaultdict
from osmox import config

root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "fixtures")
)
test_config_path = os.path.join(root, "test_config.json")


@pytest.fixture
def valid_config():
    return {
    "filter": {
        "building": [
            "house",
            "yes"
        ],
        "public_transport": ["*"],
        "highway": ["bus_stop"]
    },

    "object_features": ["units", "levels", "area", "floor_area"],

    "distance_to_nearest": ["transit", "shop"],

    "default_activities": ["home"],

    "activity_mapping": {
        "building": {
            "house": ["home"],
        },
        "amenity": {
            "pub": ["social", "work", "delivery"],
            "fast_food": ["work", "delivery", "food_shop"],
        },
        "landuse": {
            "commercial": ["shop", "work", "delivery"],
            "residential": ["home"],
        },
        "shop": {
            "*": ["shop", "work"]
        },
        "public_transport": {
            "*": ["transit"]
        },
        "highway": {
            "bus_stop": ["transit"]
        }
    }
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
        "transit"
        }


def test_valid_config(caplog, valid_config):
    config.validate_activity_config(valid_config)
    assert "['delivery', 'food_shop', 'home', 'shop', 'social', 'transit', 'work']" in caplog.text