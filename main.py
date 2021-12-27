from PIL import Image
import logging
import random
import copy
import yaml
import os

LOGGER_FILE = 'execution.log'
CONFIG_FILE = 'config.yaml'
RESOURCE_FOLDER = 'resource'
RESULT_FOLDER = 'result'
PNG_EXT = '.png'

logging.basicConfig(filename=LOGGER_FILE, level=logging.DEBUG)


def get_obj_names(type_name):
    return os.listdir(f'{RESOURCE_FOLDER}/{type_name}')


def get_canonical_obj_name(type_name, obj):
    # obj expected to have proper extension
    return f'{RESOURCE_FOLDER}/{type_name}/{obj}'


def save_img(img, name, remainder):
    # Name without extension exptected
    img.save(f'{RESULT_FOLDER}/{name}{PNG_EXT}')
    logging.info(f'Generated {name}, {remainder - 1} remaining')


def brute_force_gen(objects, to_create, accumulator=None, name=''):
    """
    Returns number of emojis that are to be created
    """
    if not objects:
        save_img(accumulator, name, to_create - 1)
        return to_create - 1

    type_name = list(objects[0].keys())[0]
    for i, obj in enumerate(get_obj_names(type_name)):
        this_obj = Image.open(get_canonical_obj_name(type_name, obj))
        new_acc = copy.copy(accumulator) or this_obj
        if to_create != 0:
            to_create = brute_force_gen(objects=objects[1:],
                                        to_create=to_create,
                                        accumulator=Image.alpha_composite(new_acc, this_obj),
                                        name=f'{name}-{obj[0:-4]}' if name else obj[0:-4])
    return to_create


def generate_randomly(config):
    random.seed(config['seed'])
    result = [[] for _ in range(len(config['objects']))]
    for i, type_dict in enumerate(config['objects']):
        for type_name, rules in type_dict.items():
            obj_names = set(get_obj_names(type_name))

            for rule_dict in rules or []:
                # Exactly name and percentage
                assert len(rule_dict) == 2
                (_, obj_name), (_, perc) = rule_dict.items()
                obj_names.discard(obj_name + PNG_EXT)
                for _ in range(config['count'] * perc // 100):
                    result[i].append(get_canonical_obj_name(type_name, obj_name + PNG_EXT))

            assert config['count'] - len(result[i]) >= 0
            if config['count'] - len(result[i]) != 0:
                # Because random.choices expects non-empty population
                result[i].extend(random.choices(list(map(lambda x: get_canonical_obj_name(type_name, x), obj_names)),
                                                k=config['count'] - len(result[i])))
            random.shuffle(result[i])
            assert len(result[i]) == config['count']

    for i in range(config['count']):
        accumulator = None
        name = ''
        for type_list in result:
            this_obj = Image.open(type_list[i])
            cur_name = type_list[i].split('/')[2][:-4]
            name = f"{name}-{cur_name}" if name else cur_name
            accumulator = accumulator or this_obj
            accumulator = Image.alpha_composite(accumulator, this_obj)
        save_img(accumulator, name, i - config['count'] - 1)


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
        if not config['random']:
            brute_force_gen(objects=config['objects'],
                            to_create=config['count'])
        else:
            generate_randomly(config)


if __name__ == '__main__':
    run()
