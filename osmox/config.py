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

def validate_activity_config(config):

    activity_config = config["activity_mapping"]    
    if activity_config:
        acts = get_acts(config)
        logger.warning(f"Configured activities: {sorted(acts)}")

    else:
        logger.error(f"No 'activity_config' found in config.")

    if config.get("features_config"):
        available = set(build.AVAILABLE_FEATURES)
        unsupported = set(config.get("features_config")) - available
        if unsupported:
            logger.error(f"Unsupported features in config: {unsupported}, please choose from: {available}.")
