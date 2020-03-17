"""
Defines the main Quinfig class.
"""

from common.cerberus import *
from common.gin import *
from common.utils import *

# Register all schemas
create_and_register_schemas()


class Quinfig(Munch):
    """
    The Quinfig class for creating configuration files.

    Quinfig provides a simple abstraction for configuration files with several useful features:
    - write (arbitrarily nested) configuration files in YAML or just specify them as dictionaries in Python
    - access keys with dot access
    - validate your configs against schemas using Cerberus
    - set fn arguments using gin
    """

    def __init__(self,
                 config_path=None,
                 schema_path=None,
                 config=None,
                 schema=None
                 ):

        # Prepare the config
        config = prepare_config(config_path=config_path,
                                schema_path=schema_path,
                                config=config,
                                schema=schema)

        # Create the Quinfig
        super(Quinfig, self).__init__(config)

    def __repr__(self):
        """
        Use a yaml dump to create a formatted representation for the Quinfig.
        """
        return f'Quinfig\n' \
               f'-------\n' \
               f'{yaml.dump(self.__dict__)}'


def prepare_config(config_path=None,
                   schema_path=None,
                   config=None,
                   schema=None) -> Munch:
    """
    Takes in paths to config and schema files.
    Validates the config against the schema, normalizes the config, parses gin and converts the config to a Munch.
    """
    # Load up the config
    if config is None:
        assert config_path is not None, 'Please pass in either config or config_path.'
        assert config_path.endswith('.yaml'), 'Must use a YAML file for the config.'
        config = yaml.load(open(config_path),
                           Loader=yaml.FullLoader)

    # Convert config to Munch: iffy ensures that the Munch fn is only applied to mappings
    config = walk_values_rec(iffy(is_mapping, lambda c: Munch(**c)), config)

    # Load up the schema
    if schema is None:
        assert schema_path is not None, 'Please pass in either schema or schema_path.'
        assert schema_path.endswith('.yaml'), 'Must use a YAML file for the config.'
        schema = yaml.load(open(schema_path),
                           Loader=yaml.FullLoader)

    # Allow gin configuration at any level of nesting: put a gin tag at every level of the schema
    schema = autoexpand_schema(schema)

    # Validate the config against the schema
    validate_config(config, schema)

    # Normalize the config
    config = normalize_config(config, schema)

    # Parse and load the gin configuration
    nested_gin_dict_parser(config)

    return config