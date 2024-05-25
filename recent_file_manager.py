import os
import configparser

recent_files_file = 'recent_files.ini'

def load_recent_files():
    config = configparser.ConfigParser()
    if os.path.exists(recent_files_file):
        config.read(recent_files_file)
    files = []
    if 'Files' in config:
        for key in sorted(config['Files'], key=lambda k: int(k.split('_')[1])):
            files.append(config['Files'][key])
    return files

def save_recent_files(files):
    config = configparser.ConfigParser()
    if 'Files' not in config:
        config['Files'] = {}
    for i, filepath in enumerate(files):
        config['Files'][f'file_{i}'] = filepath
    with open(recent_files_file, 'w') as configfile:
        config.write(configfile)
