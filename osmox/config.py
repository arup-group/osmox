import json
import logging


logger = logging.getLogger(__name__)


def load(config_path):   
    logger.warning(f"Loading config from '{config_path}'.")
    with open(config_path, "r") as read_file:
        return json.load(read_file)
    

def parse(config):

    activity_mapping = config["activity_mapping"]
    features_config = config["features_config"]


def validate_activity_config(config):

    activity_mapping = config["activity_mapping"]    
    if activity_mapping:
        acts = set()
        for _tag_key, t_dict in activity_mapping.items():
            for _t_value, act_list in t_dict.items():
                for act in act_list:
                    acts.add(act)

        logger.warning(f"Configured activities: {sorted(acts)}")

    else:
        logger.error(f"No 'activity_mapping' found in config.")

