#!/usr/bin/env python

import argparse
import json
import logging
import os
import re
import sys

import pysam
# from gdcdictionary import gdcdictionary
# from dictionaryutils import dictionary

# dictionary.init(gdcdictionary)

def resolve_platform_unit(platform_unit):
    if not platform_unit:
        return None
    pu_2dot_regex = r"(.*)\.(.*)\.(.*)"
    pu_1dot_regex = r"(.*)\.(.*)"
    pu_dict = None
    result2 = re.search(pu_2dot_regex, platform_unit)
    if result2:
        flow_cell_barcode = result2.group(1)
        lane_number = result2.group(1)
        multiplex_barcode = result2.group(3)
        if lane_number.isdigit():
            pu_dict = dict()
            pu_dict['FB'] = flow_cell_barcode
            pu_dict['LN'] = int(lane_number)
            pu_dict['MB'] = multiplex_barcode
    else:
        result1 = re.search(pu_1dot_regex, platform_unit)
        if result1:
            flow_cell_barcode = result2.group(1)
            lane_number = result2.group(2)
            if lane_number.isdigit():
                pu_dict = dict()
                pu_dict['FB'] = flow_cell_barcode
                pu_dict['LN'] = int(lane_number)
    return pu_dict

def extract_readgroup_json(bam_path, logger):
    step_dir = os.getcwd()
    bam_file = os.path.basename(bam_path)
    bam_name, bam_ext = os.path.splitext(bam_file)
    readgroups_json_file = bam_name+'.json'
    samfile = pysam.AlignmentFile(bam_path, 'rb', check_header=True, check_sq=False)
    samfile_header = samfile.header
    bam_readgroup_dict_list = samfile_header.get('RG')
    out_readgroup_dict_list = list()
    
    if len(bam_readgroup_dict_list) < 1:
        logger.info('There are no readgroups in BAM: {}'.format(bam_name))
        sys.exit(1)
    else:
        for bam_readgroup_dict in bam_readgroup_dict_list:
            logger.debug('bam_readgroup_dict: {}'.format(bam_readgroup_dict))
            readgroup_meta = dict()
            readgroup_meta['aliquots'] = dict()
            readgroup_meta['aliquots']['submitter_id'] = bam_readgroup_dict.get('SM', 'REQUIRED<string>')
            readgroup_meta['library_name'] = bam_readgroup_dict.get('LB', 'REQUIRED<string>')
            readgroup_meta['platform'] = bam_readgroup_dict.get('PL', 'REQUIRED<enumeration>')
            readgroup_meta['read_group_name'] = bam_readgroup_dict.get('ID', 'REQUIRED<string>')
            readgroup_meta['sequencing_center'] = bam_readgroup_dict.get('CN', 'REQUIRED<string>')
            if readgroup_meta['aliquots']['submitter_id'] != 'REQUIRED<string>':
                readgroup_meta['submitter_id'] = readgroup_meta['aliquots']['submitter_id']+'_'+readgroup_meta['read_group_name']
            else:
                readgroup_meta['submitter_id'] = 'REQUIRED<string>'
            readgroup_meta['experiment_name'] = 'REQUIRED<string>'
            readgroup_meta['is_paired_end'] = 'REQUIRED<boolean>'
            readgroup_meta['library_selection'] = 'REQUIRED<enumeration>'
            readgroup_meta['library_strategy'] = 'REQUIRED<enumeration>'
            readgroup_meta['read_length'] = 'REQUIRED<integer,null>'
            readgroup_meta['target_capture_kit'] = 'REQUIRED<enumeration>'

            # possible use
            barcode_sequence = bam_readgroup_dict.get('BC', None) # CHECK_MATCH with multiplex_barcode, if present, below
            description = bam_readgroup_dict.get('DS', None) # experiment?

            predicted_median_insert_size = bam_readgroup_dict.get('PI', None)
            readgroup_meta['instrument_model'] = bam_readgroup_dict.get('PM', 'OPTIONAL<enumeration>')
            readgroup_meta['sequencing_date'] = bam_readgroup_dict.get('DT', 'OPTIONAL<ISO8601 date or date/time, null>')

            platform_unit = bam_readgroup_dict.get('PU', None)
            pu_dict = resolve_platform_unit(platform_unit)
            if pu_dict:
                readgroup_meta['flow_cell_barcode'] = pu_dict.get('FB', 'OPTIONAL<string>')
                readgroup_meta['lane_number'] = pu_dict.get('LN', 'OPTIONAL<integer>')
                readgroup_meta['multiplex_barcode'] = pu_dict.get('MB', 'OPTIONAL<string>')

                #CHECK_MATCH
                if barcode_sequence and readgroup_meta['multiplex_barcode'] != 'OPTIONAL<string>':
                    if barcode_sequence != readgroup_meta['multiplex_barcode']:
                        logger.info('In Read Group {0}, the BC tag ({1}) does not match the third dotted part of the PU tag ({2})'.format(
                            readgroup_meta['read_group_name'], barcode_sequence, readgroup_meta['multiplex_barcode']))
            else:
                readgroup_meta['flow_cell_barcode'] = 'OPTIONAL<string>'
                readgroup_meta['lane_number'] = 'OPTIONAL<integer>'
                readgroup_meta['multiplex_barcode'] = 'OPTIONAL<string>'

            readgroup_meta['RIN'] = 'OPTIONAL<number>'
            readgroup_meta['adapter_name'] = 'OPTIONAL<string>'
            readgroup_meta['adapter_sequence'] = 'OPTIONAL<string>'
            readgroup_meta['base_caller_name'] = 'OPTIONAL<string>'
            readgroup_meta['base_caller_version'] = 'OPTIONAL<string>'
            readgroup_meta['days_to_sequencing'] = 'OPTIONAL<integer>'
            readgroup_meta['fragment_maximum_length'] = 'OPTIONAL<integer>'
            readgroup_meta['fragment_mean_length'] = 'OPTIONAL<number>'
            readgroup_meta['fragment_minimum_length'] = 'OPTIONAL<integer>'
            readgroup_meta['fragment_standard_deviation_length'] = 'OPTIONAL<number>'
            readgroup_meta['includes_spike_ins'] = 'OPTIONAL<boolean>'
            readgroup_meta['library_preparation_kit_catalog_number'] = 'OPTIONAL<string>'
            readgroup_meta['library_preparation_kit_name'] = 'OPTIONAL<string>'
            readgroup_meta['library_preparation_kit_vendor'] = 'OPTIONAL<string>'
            readgroup_meta['library_preparation_kit_version'] = 'OPTIONAL<string>'
            readgroup_meta['library_strand'] = 'OPTIONAL<enumeration>'
            readgroup_meta['size_selection_range'] = 'OPTIONAL<string>'
            readgroup_meta['spike_ins_concentration'] = 'OPTIONAL<string>'
            readgroup_meta['spike_ins_fasta'] = 'OPTIONAL<string>'
            readgroup_meta['to_trim_adapter_sequence'] = 'OPTIONAL<boolean>'
            readgroup_meta['type'] = 'read_group'
            out_readgroup_dict_list.append(readgroup_meta)

    with open(readgroups_json_file, 'w') as f:
        json.dump(out_readgroup_dict_list, f, indent=4)
    return

def validate_inputs(bam_path, logger):
    bam_file = os.path.basename(bam_path)
    bam_name, bam_ext = os.path.splitext(bam_file)
    if bam_ext != '.bam':
        logger.info("This program only runs on BAM files, which must have the file suffix '.bam'")
        sys.exit(1)
    return

def setup_logging(args):
    logging.basicConfig(
        #filename=os.path.join('output.log'),
        level=args.level,
        filemode='w',
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d_%H:%M:%S_%Z',
    )
    logger = logging.getLogger(__name__)
    return logger

def main():
    parser = argparse.ArgumentParser('convert readgroups to json')

    # Logging flags.
    parser.add_argument('-d', '--debug',
        action = 'store_const',
        const = logging.DEBUG,
        dest = 'level',
        help = 'Enable debug logging.',
    )
    parser.set_defaults(level = logging.INFO)

    # Required flags.
    parser.add_argument('-b', '--bam_path',
                        required = True,
                        help = 'BAM file.'
    )
    # parser.add_argument('-d', '--detailed_id_verify',
    #                     required = False,
    #                     help = 'Checks that each sequenced readgroup ID is represented in the header. Much slower.'
    # )
    

    args = parser.parse_args()
    bam_path = args.bam_path

    logger = setup_logging(args)

    validate_inputs(bam_path, logger)
    extract_readgroup_json(bam_path, logger)
    return

if __name__ == '__main__':
    main()
