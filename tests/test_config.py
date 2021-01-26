import os
from collections import defaultdict
from osmbx import config

root = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "fixtures")
)
test_config_path = os.path.join(root, "test_config.json")


def test_load_config():
    cnfg = config.load(test_config_path)
    assert cnfg
    assert isinstance(cnfg, dict)
