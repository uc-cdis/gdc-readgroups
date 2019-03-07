import csv
import json
import os

def get_readgroup_template():
    json_file = 'readgroup_template.json'
    cwd = os.path.dirname(os.path.realpath(__file__))
    json_path = os.path.join(cwd, json_file)
    with open(json_path, 'r') as f_open:
        data = json.load(f_open)
    return data

def get_tsv_header(data, logger):
    header = list()
    for item in data.keys():
        if isinstance(data[item],dict):
            subvalue_list = list(data[item].keys())
            assert len(subvalue_list) == 1
            subvalue = subvalue_list[0]
            header.append('.'.join([item, subvalue]))
        elif isinstance(data[item],int):
            header.append(item)
        elif isinstance(data[item],str):
            header.append(item)
        else:
            logger.error('unexpected type with item {0}, of type {1}'.format(data[item],
                                                                             type(data[item])))
            raise ValueError
    return header

def get_tsv_values(data, logger):
    row = list()
    for item in data.keys():
        if isinstance(data[item],dict):
            subvalue_list = list(data[item].keys())
            assert len(subvalue_list) == 1
            subvalue = subvalue_list[0]
            row.append(data[item][subvalue])
        elif isinstance(data[item],int):
            row.append(data[item])
        elif isinstance(data[item],str):
            row.append(data[item])
        else:
            logger.error('unexpected type with item {0}, of type {1}'.format(data[item],
                                                                             type(data[item])))
            raise ValueError
    return row

def write_readgroups(output, out_file, logger):
    output_format = out_file.split('.')[-1]
    if output_format == 'json':
        with open(out_file, 'w') as f_open:
            json.dump(output, f_open, indent=4)
    elif output_format == 'tsv':
        with open(out_file, 'wt') as f_open:
            tsv_writer = csv.writer(f_open, delimiter='\t')
            tsv_header = get_tsv_header(output[0], logger)
            tsv_writer.writerow(tsv_header)
            for item in output:
                tsv_row = get_tsv_values(item, logger)
                tsv_writer.writerow(tsv_row)
    else:
        logger.error('Invalid output_format: {}'.format(output_format))
        raise ValueError
    return
