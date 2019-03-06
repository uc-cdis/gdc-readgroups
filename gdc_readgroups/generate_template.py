from gdc_readgroups.util import get_readgroup_template, write_readgroups

def generate_template(output_format, logger):
    out_file_base = 'gdc_readgroups'
    out_file = '.'.join([out_file_base, output_format])
    data = get_readgroup_template()
    output = [data, data]
    write_readgroups(output, out_file, logger)
    return out_file
