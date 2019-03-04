import json
import os

def get_readgroup_template():
    cwd = os.path.dirname(os.path.realpath(__file__))
    json_path = os.path.join(cwd, 'readgroup_template.json')
    with open(json_path, 'r') as f_open:
        data = json.load(f_open)
    return data

def generate_template_json(logger):
    json_data = get_readgroup_template()
    output = list()
    output.append(json_data)
    output.append(json_data)
    with open('gdc_readgroups.json', 'w') as f_open:
        json.dump(output, f_open, indent=4)
    return output
