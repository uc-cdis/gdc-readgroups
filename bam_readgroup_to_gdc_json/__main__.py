#!/usr/bin/env python
"""

This package takes a BAM as input and converts each readgroup
to a json object needed to create a GDC Read Group node.
"""
import argparse
import logging
import os

from bam_readgroup_to_gdc_json.extract_readgroup import extract_readgroup_json
from bam_readgroup_to_gdc_json.exceptions import NotABamError
from bam_readgroup_to_gdc_json.generate_template import generate_template_json

def output_help():
    import textwrap
    helpdesc = 'This package will extract the Read Group header lines from a BAM file, and convert the contained metadata to a json file with appropriate values applied for creation of a Read Group node in the Genomic Data Commons (GDC).'
    print('\n' + textwrap.fill(helpdesc) + '\n' \
          'Usage\n' +
          '\tbam_readgroup_to_gdc_json [--bam_path <file.bam> | --template | --version]')
    return

def output_version():
    import inspect
    import pkg_resources
    s = inspect.stack()
    package = inspect.getmodule(s[1][0]).__name__.split('.')[0]
    version = pkg_resources.require(package)[0].version
    print(package + ' ' + version)
    return

def validate_input(bam_path, logger):
    """

    :param bam_path:
    :param logger:
    :rtype: None
    :return:
    """
    bam_file = os.path.basename(bam_path)
    _, bam_ext = os.path.splitext(bam_file)
    if bam_ext != '.bam':
        logger.error("This program only runs on BAM files, which must have the file suffix '.bam'")
        raise NotABamError
    return

def setup_logging(args):
    """

    :param args:
    :rtype: logging.RootLogger
    :return:
    """
    logging.basicConfig(
        level=args.level,
        filemode='w',
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d_%H:%M:%S_%Z')
    logger = logging.getLogger(__name__)
    return logger

def main():
    """

    :return:
    """
    parser = argparse.ArgumentParser('convert readgroups to json')
    parser.add_argument('-d', '--debug',
                        action='store_const',
                        const=logging.DEBUG,
                        dest='level',
                        help='Enable debug logging.')
    parser.set_defaults(level=logging.INFO)
    parser.add_argument('-b', '--bam_path',
                        required=False,
                        help='BAM file.')
    parser.add_argument('-t', '--template',
                        action='store_true',
                        required=False,
                        help='write json template with two Read Groups')
    parser.add_argument('-v', '--version',
                        action='store_true',
                        required=False,
                        help='Output program version.')
    args = parser.parse_args()
    bam_path = args.bam_path
    template = args.template
    version = args.version
    logger = setup_logging(args)

    if version:
        output_version()
    elif bam_path:
        validate_input(bam_path, logger)
        extract_readgroup_json(bam_path, logger)
    elif template:
        generate_template_json()
    else:
        output_help()
    return

if __name__ == '__main__':
    main()
