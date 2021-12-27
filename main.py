from PIL import Image
import logging
import copy
import yaml
import os

LOGGER_FILE = 'execution.log'
CONFIG_FILE = 'config.yaml'
RESOURCE_FOLDER = 'resource'
RESULT_FOLDER = 'result'
created = 0

logging.basicConfig(filename=LOGGER_FILE, level=logging.DEBUG)


def brute_force_gen(objects, count=-1, accumulator=None, name='0'):
    global created
    if created == count:
        return

    if not objects:
        created += 1
        accumulator.save(f'{RESULT_FOLDER}/{name}.png')
        logging.info(f'Generated {name}, {count - created} remaining')
        return

    for i, obj in enumerate(os.listdir(f'{RESOURCE_FOLDER}/{objects[0]}')):
        this_obj = Image.open(f'{RESOURCE_FOLDER}/{objects[0]}/{obj}')
        new_acc = copy.copy(accumulator) or this_obj
        brute_force_gen(objects=objects[1:],
                        count=count,
                        accumulator=Image.alpha_composite(new_acc, this_obj),
                        name=f'{name}-{i}')


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
                        count=config['count'])


if __name__ == '__main__':
    run()
