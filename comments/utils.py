import os

import yaml

CONFIG_FILE_DEFAULT_PATH = 'config.yaml'


def parse_config_file(config_file_path=None):

    config_file_path = os.path.abspath(
        config_file_path or CONFIG_FILE_DEFAULT_PATH
    )

    with open(config_file_path, 'r') as config_file:
        try:
            config = yaml.load(config_file)
        except yaml.YAMLError as error:
            error.note = (
                f'\nError on reading config file: {config_file_path}\n'
            )
            raise error
        else:
            if not isinstance(config, dict):
                raise TypeError('Config file must contain dict')
            return config
