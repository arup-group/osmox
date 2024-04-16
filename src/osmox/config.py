import importlib
import json
import logging

import jsonschema

logger = logging.getLogger(__name__)
SCHEMA_FILE = importlib.resources.files("osmox") / "schema.json"
with importlib.resources.as_file(SCHEMA_FILE) as f:
    SCHEMA = json.load(f.open())


def load(config_path):
    logger.warning(f"Loading config from '{config_path}'.")
    with open(config_path, "r") as read_file:
        return json.load(read_file)


def validate(config):
    validator = jsonschema.Draft202012Validator
    validator.META_SCHEMA["unevaluatedProperties"] = False
    validator.check_schema(SCHEMA)
    jsonschema.validate(config, SCHEMA)


def get_acts(config):
    activity_config = config.get("activity_mapping")
    if activity_config:
        acts = set()
        for _tag_key, t_dict in activity_config.items():
            for _t_value, act_list in t_dict.items():
                for act in act_list:
                    acts.add(act)

        return acts
    return set([])


def get_tags(config):
    filter_config = config.get("filter")
    if filter_config:
        keys = set()
        tags = set()
        for tag_key, tag_values in filter_config.items():
            keys.add(tag_key)
            for tag_value in tag_values:
                tags.add((tag_key, tag_value))

        return keys, tags
    return set([]), set([])


def validate_activity_config(config):
    validate(config)
    keys, tags = get_tags(config)
    logger.warning(f"Configured OSM tag keys: {sorted(keys)}")

    acts = get_acts(config)
    logger.warning(f"Configured activities: {sorted(acts)}")

    if "distance_to_nearest" in config:
        act_diff = set(config["distance_to_nearest"]).difference(acts)
        if act_diff:
            raise ValueError(f"'Distance to nearest' has non-configured activities: {act_diff}")

    if "fill_missing_activities" in config:
        for group in config["fill_missing_activities"]:
            act_diff = set(group.get("required_acts", [])).difference(acts)
            if act_diff:
                raise ValueError(
                    f"'Fill missing activities' group has non-configured activities: {act_diff}"
                )
