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

def validate_inputs(bam_path, logger):
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
    # Logging flags.
    parser.add_argument('-d', '--debug',
                        action='store_const',
                        const=logging.DEBUG,
                        dest='level',
                        help='Enable debug logging.')
    parser.set_defaults(level=logging.INFO)
    # Required flags.
    parser.add_argument('-b', '--bam_path',
                        required=True,
                        help='BAM file.')
    args = parser.parse_args()
    bam_path = args.bam_path
    logger = setup_logging(args)

    validate_inputs(bam_path, logger)
    extract_readgroup_json(bam_path, logger)
    return

if __name__ == '__main__':
    main()
