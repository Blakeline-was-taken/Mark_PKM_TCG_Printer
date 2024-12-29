import toml
import logging
import os

logging.basicConfig(filename='error.log', level=logging.ERROR,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if not os.path.exists('config.toml'):
    logging.error('config.toml not found')
    raise FileNotFoundError('config.toml not found')

with open('config.toml', 'r') as f:
    config = toml.load(f)

    config['base_colors'] = [tuple(c) for c in config['base_colors']]

    if not os.path.exists(config["cards_file_path"]):
        logging.error('Cards file not found.')
        raise FileNotFoundError(config["cards_file_path"])
