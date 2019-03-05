import json
import os

def get_readgroup_template():
    json_file = 'readgroup_template.json'
    cwd = os.path.dirname(os.path.realpath(__file__))
    json_path = os.path.join(cwd, json_file)
    with open(json_path, 'r') as f_open:
        data = json.load(f_open)
    return data

def generate_template_json():
    json_file = 'gdc_readgroups.json'
    data = get_readgroup_template()
    output = [data, data]
    with open(json_file, 'w') as f_open:
        json.dump(output, f_open, indent=4)
    return json_file
