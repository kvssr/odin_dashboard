import sys
from ruamel.yaml import YAML
yaml = YAML(typ='safe')

def load_config_file(db):
    with open('config.yaml', 'r') as file:
        print('loading config..')
        layout_config = yaml.load(file)
    
    stats_names = layout_config['model_names_list']
    stats_all = {}

    for stat in stats_names:
        for n in db.Model.registry.mappers:
            if n.class_.__name__ == stat:
                model = n.class_
                stats_all[stat] = model

    layout_config['model_list'] = stats_all
    print('Config loaded successfully')
    return layout_config


def save_config_to_file(config, filename):
    temp = config.copy()
    temp['model_list'] = None
    yaml.indent(mapping=2, sequence=2, offset=0)
    with open(filename, 'w') as file:
        yaml.dump(temp, file)
        print('Config Saved Successfully')


def load_file(filename:str) -> dict:
    with open(filename, 'r') as file:
        print(f'loading file: {filename}')
        db_data = yaml.load(file)
    return db_data
