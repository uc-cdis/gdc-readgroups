import json
import os
import re
import sys

from dateutil import parser
import pysam

from bam_readgroup_to_gdc_json.exceptions import NoReadGroupError, InvalidPlatformError, InvalidPlatformModelError, MissingReadgroupIdError, InvalidDatetimeError, NotABamError

def resolve_platform_unit(platform_unit):
    if not platform_unit:
        return None
    pu_2dot_regex = r"(.*)\.(.*)\.(.*)"
    pu_1dot_regex = r"(.*)\.(.*)"
    pu_dict = None
    result2 = re.search(pu_2dot_regex, platform_unit)
    if result2:
        flow_cell_barcode = result2.group(1)
        lane_number = result2.group(2)
        multiplex_barcode = result2.group(3)
        if lane_number.isdigit():
            pu_dict = dict()
            pu_dict['FB'] = flow_cell_barcode
            pu_dict['LN'] = int(lane_number)
            pu_dict['MB'] = multiplex_barcode
    else:
        result1 = re.search(pu_1dot_regex, platform_unit)
        if result1:
            flow_cell_barcode = result1.group(1)
            lane_number = result1.group(2)
            if lane_number.isdigit():
                pu_dict = dict()
                pu_dict['FB'] = flow_cell_barcode
                pu_dict['LN'] = int(lane_number)
    return pu_dict

def get_platform(readgroup_dict, logger):
    if not 'PL' in readgroup_dict:
        return None
    pl = readgroup_dict['PL'].lower()
    if 'illumina' in pl:
        platform = 'Illumina'
    elif 'solid' in pl:
        platform = 'SOLiD'
    elif '454' in pl:
        platform = 'LS454'
    elif all(x in pl for x in ('ion', 'torrent')):
        platform = 'Ion Torrent'
    elif all(x in pl for x in ('complete', 'genomics')):
        platform = 'Complete Genomics'
    elif all(x in pl for x in ('pac', 'bio')):
        platform = 'PacBio'
    elif 'other' in pl:
        platform = 'Other'
    elif pl in ('capillary', 'helicos', 'ont'): #in the SAM specification
        platform = 'Other'
    else:
        logger.error('The read group {0} has an unrecognized PL (platform) value of: {1}'.format(readgroup_dict['ID'], readgroup_dict['PL']))
        logger.error('Accepted values include:\n'
                     + '\t Illumina\n'
                     + '\t SOLiD\n'
                     + '\t LS454\n'
                     + '\t Ion Torrent\n'
                     + '\t Complete Genomics\n'
                     + '\t PacBio\n'
                     + '\t Other\n')
        raise InvalidPlatformError
    return platform

def get_platform_model(readgroup_dict, logger):
    if not 'PM' in readgroup_dict:
        return None
    pm = readgroup_dict['PM'].lower().strip().replace(' ','').replace('-','').replace('_','').replace('.','').replace(',','')
    if '454' in pm and any(x in pm for x in ('gs', 'flx', 'titanium')):
        platform_model = '454 GS FLX Titanium'
    elif all(x in pm for x in ('solid', '2')):
        platform_model = 'AB SOLiD 2'
    elif all(x in pm for x in ('solid', '3')):
        platform_model = 'AB SOLiD 3'
    elif all(x in pm for x in ('solid', '4')):
        platform_model = 'AB SOLiD 4'
    elif all(x in pm for x in ('complete', 'genomics')):
        platform_model = 'Complete Genomics'
    elif all(x in pm for x in ('illumina', 'hiseq', 'x')) and any(x in pm for x in ('10', 'ten')):
        platform_model = 'Illumina HiSeq X Ten'
    elif all(x in pm for x in ('illumina', 'hiseq', 'x')) and any(x in pm for x in ('5', 'five')):
        platform_model = 'Illumina HiSeq X Five'
    elif all (x in pm for x in ('illumina', 'iix')):
        platform_model = 'Illumina Genome Analyzer IIx'
    elif all (x in pm for x in ('illumina', 'ii')):
        platform_model = 'Illumina Genome Analyzer II'
    elif all (x in pm for x in ('illumina', '2000')):
        platform_model = 'Illumina HiSeq 2000'
    elif all (x in pm for x in ('illumina', '2500')):
        platform_model = 'Illumina HiSeq 2500'
    elif all (x in pm for x in ('illumina', '4000')):
        platform_model = 'Illumina HiSeq 4000'
    elif all (x in pm for x in ('illumina', 'miseq')):
        platform_model = 'Illumina MiSeq'
    elif all (x in pm for x in ('ion', 'torrent', 'pgm')):
        platform_model = 'Ion Torrent PGM'
    elif all (x in pm for x in ('ion', 'torrent', 'proton')):
        platform_model = 'Ion Torrent Proton'
    elif 'pacbio' in pm:
        platform_model = 'PacBio RS'
    else:
        logger.error('The read group {0} has an unrecognized PL (platform) value of: {1}'.format(readgroup_dict['ID'], readgroup_dict['PL']))
        logger.error('Accepted values include:\n'
                     + '\t 454 GS FLX Titanium\n'
                     + '\t AB SOLiD 2\n'
                     + '\t AB SOLiD 3\n'
                     + '\t AB SOLiD 4\n'
                     + '\t Complete Genomics\n'
                     + '\t Illumina HiSeq X Ten\n'
                     + '\t Illumina HiSeq X Five\n'
                     + '\t Illumina Genome Analyzer II\n'
                     + '\t Illumina Genome Analyzer IIx\n'
                     + '\t Illumina HiSeq 2000\n'
                     + '\t Illumina HiSeq 2500\n'
                     + '\t Illumina HiSeq 4000\n'
                     + '\t Illumina MiSeq\n'
                     + '\t Illumina NextSeq\n'
                     + '\t Ion Torrent PGM\n'
                     + '\t Ion Torrent Proton\n'
                     + '\t PacBio RS\n'
                     + '\t Other')
        raise InvalidPlatformModelError
    return platform_model

def get_datetime(readgroup_dict, logger):
    if not 'DT' in readgroup_dict:
        return None
    try:
        dt = parser.parse(readgroup_dict['DT'])
    except (ValueError, TypeError) as e:
        logger.error('The read group {0} has an unrecognized DT (datetime) value of: {1}'.format(readgroup_dict['ID'], readgroup_dict['DT']))
        raise InvalidDatetimeError
    return dt.isoformat()

def harmonize_readgroup(readgroup_dict, logger):
    if not 'ID' in readgroup_dict:
        logger.error('"ID" is missing from readgroup: {}'.format(readgroup_dict))
        raise MissingReadgroupIdError
    pl = get_platform(readgroup_dict, logger)
    pm = get_platform_model(readgroup_dict, logger)
    dt = get_datetime(readgroup_dict, logger)
    if pl:
        readgroup_dict['PL'] = pl
    if pm:
        readgroup_dict['PM'] = pm
    if dt:
        readgroup_dict['DT'] = dt
    return readgroup_dict

def get_readgroup_dict_list(bam_readgroup_dict_list, logger):
    out_readgroup_dict_list = list()
    for bam_readgroup_dict in bam_readgroup_dict_list:
        rg = harmonize_readgroup(bam_readgroup_dict, logger)
        readgroup_meta = dict()
        readgroup_meta['aliquots'] = dict()
        readgroup_meta['aliquots']['submitter_id'] = rg.get('SM', 'REQUIRED<string>')
        readgroup_meta['experiment_name'] = rg.get('DS', 'REQUIRED<string>')
        readgroup_meta['library_name'] = rg.get('LB', 'REQUIRED<string>')
        readgroup_meta['platform'] = rg.get('PL', 'REQUIRED<enumeration>')
        readgroup_meta['read_group_name'] = rg.get('ID', 'REQUIRED<string>')
        readgroup_meta['sequencing_center'] = rg.get('CN', 'REQUIRED<string>')
        if readgroup_meta['aliquots']['submitter_id'] != 'REQUIRED<string>':
            readgroup_meta['submitter_id'] = readgroup_meta['aliquots']['submitter_id']+'_'+readgroup_meta['read_group_name']
        else:
            readgroup_meta['submitter_id'] = 'REQUIRED<string>'
        readgroup_meta['is_paired_end'] = 'REQUIRED<boolean>'
        readgroup_meta['library_selection'] = 'REQUIRED<enumeration>'
        readgroup_meta['library_strategy'] = 'REQUIRED<enumeration>'
        readgroup_meta['read_length'] = 'REQUIRED<integer,null>'
        readgroup_meta['target_capture_kit'] = 'REQUIRED<enumeration>'

        # possible use
        barcode_sequence = rg.get('BC', None) # CHECK_MATCH with multiplex_barcode, if present, below

        predicted_median_insert_size = rg.get('PI', None)
        readgroup_meta['instrument_model'] = rg.get('PM', 'OPTIONAL<enumeration>')
        readgroup_meta['sequencing_date'] = rg.get('DT', 'OPTIONAL<ISO8601 date or date/time, null>')

        platform_unit = rg.get('PU', None)
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
    return out_readgroup_dict_list

def extract_readgroup_json(bam_path, logger):
    bam_file = os.path.basename(bam_path)
    bam_name, bam_ext = os.path.splitext(bam_file)
    readgroups_json_file = bam_name+'.json'
    with open (bam_path) as f:
        samfile = pysam.AlignmentFile(f, 'rb', check_header=True, check_sq=False)
        if not samfile.is_bam:
            logger.error("This program only runs on BAM files.")
            raise NotABamError
        samfile_header = samfile.header
        bam_readgroup_dict_list = samfile_header.get('RG')
        if not bam_readgroup_dict_list:
            logger.error('There are no readgroups in BAM: {}'.format(samfile.filename))
            raise NoReadGroupError
        readgroup_dict_list = get_readgroup_dict_list(bam_readgroup_dict_list, logger)
    with open(readgroups_json_file, 'w') as f:
        json.dump(readgroup_dict_list, f, indent=4)
    return readgroups_json_file
