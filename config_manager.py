import configparser
import os

config_file = 'config.ini'

def load_settings():
    config = configparser.ConfigParser()
    if os.path.exists(config_file):
        config.read(config_file)
    return config

def save_settings(config):
    with open(config_file, 'w') as configfile:
        config.write(configfile)

def get_setting(section, option, fallback=None, data_type=str):
    config = load_settings()
    try:
        if data_type == int:
            return config.getint(section, option, fallback=fallback)
        elif data_type == float:
            return config.getfloat(section, option, fallback=fallback)
        elif data_type == bool:
            return config.getboolean(section, option, fallback=fallback)
        else:
            return config.get(section, option, fallback=fallback)
    except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
        return fallback

def set_setting(section, option, value):
    config = load_settings()
    if section not in config:
        config[section] = {}
    config[section][option] = str(value)
    save_settings(config)
