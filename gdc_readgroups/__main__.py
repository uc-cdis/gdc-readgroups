#!/usr/bin/env python
"""

This package takes a BAM as input and converts each readgroup
to a json object needed to create a GDC Read Group node.
"""
import argparse
import logging
import os

from gdc_readgroups.extract_readgroup import extract_readgroup
from gdc_readgroups.exceptions import NotABamError
from gdc_readgroups.generate_template import generate_template

def output_version(logger):
    import inspect
    import pkg_resources
    s = inspect.stack()
    package = inspect.getmodule(s[1][0]).__name__.split('.')[0]
    version = pkg_resources.require(package)[0].version
    logger.info('\n' + package + ' ' + version)
    return

def validate_input(bam_path, logger):
    """

    :param bam_path:
    :param output_format:
    :param template:
    :param version:
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

    parser = argparse.ArgumentParser(description='Convert BAM Read Groups to GDC Read Group Nodes')
    subparsers = parser.add_subparsers(dest='command')
    parser.add_argument('-d', '--debug',
                        action='store_const',
                        const=logging.DEBUG,
                        dest='level',
                        help='Enable debug logging.')
    parser.set_defaults(level=logging.INFO)
    parser.add_argument('-v', '--version',
                            action='store_true',
                            required=False,
                            help='Output program version.')
    parser_bam = subparsers.add_parser('bam-mode', help='using a BAM file, write GDC Read Group nodes')
    parser_bam.add_argument('-b', '--bam-path',
                            action='store',
                            required=True,
                            help='BAM file')
    parser_bam.add_argument('-f', '--output-format',
                            action='store',
                            choices=['json','tsv'],
                            default='json',
                            required=False)
    parser_template = subparsers.add_parser('template-mode', help='write template with two Read Groups')
    parser_template.add_argument('-f', '--output-format',
                            action='store',
                            choices=['json','tsv'],
                            default='json',
                            required=False)

    args = parser.parse_args()
    logger = setup_logging(args)
    if args.command:
        if args.command == 'bam-mode':
            validate_input(args.bam_path, logger)
            out_file = extract_readgroup(args.bam_path, args.output_format, logger)
            logger.info('\nwrote {}'.format(out_file))
        elif args.command == 'template-mode':
            out_file = generate_template(args.output_format, logger)
            logger.info('\nwrote {}'.format(out_file))
    elif args.version:
        output_version(logger)
    else:
        parser.print_help()
    return

if __name__ == '__main__':
    main()
