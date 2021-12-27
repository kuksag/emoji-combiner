from PIL import Image
import logging
import copy
import yaml
import os

LOGGER_FILE = 'execution.log'
CONFIG_FILE = 'config.yaml'
RESOURCE_FOLDER = 'resource'
RESULT_FOLDER = 'result'

logging.basicConfig(filename=LOGGER_FILE, level=logging.DEBUG)


def brute_force_gen(objects, to_create, accumulator=None, name='0'):
    """
    Returns number of emojis that are to be created
    """
    if not objects:
        accumulator.save(f'{RESULT_FOLDER}/{name}.png')
        logging.info(f'Generated {name}, {to_create - 1} remaining')
        return to_create - 1

    for i, obj in enumerate(os.listdir(f'{RESOURCE_FOLDER}/{objects[0]}')):
        this_obj = Image.open(f'{RESOURCE_FOLDER}/{objects[0]}/{obj}')
        new_acc = copy.copy(accumulator) or this_obj
        if to_create != 0:
            to_create = brute_force_gen(objects=objects[1:],
                                        to_create=to_create,
                                        accumulator=Image.alpha_composite(new_acc, this_obj),
                                        name=f'{name}-{i}')
    return to_create


def run():
    base_dir = os.path.dirname(os.path.realpath(__file__))

    if not os.path.exists(RESULT_FOLDER):
        logging.info(f'{RESULT_FOLDER} not found in {base_dir}, creating')
        os.makedirs(RESULT_FOLDER)

    if not os.path.exists(CONFIG_FILE):
        logging.info(f'{CONFIG_FILE} not found in {base_dir}, aborting')
        exit(1)
    else:
        logging.info(f'{CONFIG_FILE} found')

    with open(CONFIG_FILE, 'r') as _config:
        config = yaml.safe_load(_config)
        logging.info(f"Using this config:\n{config}")
        brute_force_gen(objects=config['objects'],
                        to_create=config['count'])


if __name__ == '__main__':
    run()
