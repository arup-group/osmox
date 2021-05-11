import json
import logging

from osmox import build

logger = logging.getLogger(__name__)


def load(config_path):   
    logger.warning(f"Loading config from '{config_path}'.")
    with open(config_path, "r") as read_file:
        return json.load(read_file)


def get_acts(config):
    activity_config = config["activity_mapping"]    
    if activity_config:
        acts = set()
        for _tag_key, t_dict in activity_config.items():
            for _t_value, act_list in t_dict.items():
                for act in act_list:
                    acts.add(act)

        return acts
    return set([])


def validate_activity_config(config):

    activity_mapping = config["activity_mapping"]    
    if activity_mapping:
        acts = get_acts(config)
        logger.warning(f"Configured activities: {sorted(acts)}")

    else:
        logger.error(f"No 'activity_config' found in config.")

    if config.get("features_config"):
        available = set(build.AVAILABLE_FEATURES)
        unsupported = set(config.get("features_config")) - available
        if unsupported:
            logger.error(f"Unsupported features in config: {unsupported}, please choose from: {available}.")
    
    if "distance_to_nearest" in config:
        acts = get_acts(config=config)
        for act in config["distance_to_nearest"]:
            if act not in acts:
                logger.error(
                    f"'Distance to nearest' has a non-configured activity '{act}'"
                )
    
    if "fill_missing_activities" in config:
        required_keys = {"area_tags", "required_acts", "new_tags", "size", "spacing"}
        acts = get_acts(config=config)

        for group in config["fill_missing_activities"]:
            keys = list(group)
            for k in required_keys:
                if k not in keys:
                    logger.error(
                    f"'Fill missing activities' group is missing required key: {k}"
                )
            for act in group.get("required_acts", []):
                if act not in acts:
                    logger.error(
                        f"'Fill missing activities' group has a non-configured activity '{act}'"
                    )
