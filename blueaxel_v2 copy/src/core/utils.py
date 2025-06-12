"""
Utility functions for the BlueAxel agent.
"""

import json


with open(
    "bluegen/agents/blueaxel_v2/assets/traductor.json",
    encoding="utf-8"
) as f:
    translations = json.load(f)


def get_traduction_from_key(
    key: str
) -> str:
    """
    Get the French translation for a given key from the traductor.json file.

    Args:
        key (str): The key to translate.

    Returns:
        str: The French translation of the key.
    """
    return translations.get(key, key)
