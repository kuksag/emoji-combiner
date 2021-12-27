from PIL import Image
import logging
import copy
import yaml
import os

LOGGER_FILE = 'execution.log'
CONFIG_FILE = 'config.yaml'
RESOURCE_FOLDER = 'resource'
RESULT_FOLDER = 'result'
count = 0

logging.basicConfig(filename=LOGGER_FILE, level=logging.DEBUG)


def go_merge(types, bound=-1, accumulator=None, name='0'):
    global count
    if count == bound:
        return

    if not types:
        count += 1
        accumulator.save(f'{RESULT_FOLDER}/{name}.png')
        logging.info(f'Generated {name}, {bound - count} remaining')
        return

    for i, obj in enumerate(os.listdir(f'{RESOURCE_FOLDER}/{types[0]}')):
        this_obj = Image.open(f'{RESOURCE_FOLDER}/{types[0]}/{obj}')
        new_acc = copy.copy(accumulator) or this_obj
        go_merge(types=types[1:],
                 bound=bound,
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
        types = config['objects']
        bound = config['bound']
        generator = []
        for type in types:
            generator.append(list(map(lambda x: f"{RESOURCE_FOLDER}/{type}/{x}",
                                      os.listdir(f"{RESOURCE_FOLDER}/{type}"))))
        logging.info(f"Using this bound: {bound}")
        logging.info(f'Found these types: {types}')
        go_merge(types=types, bound=bound)


if __name__ == '__main__':
    run()
