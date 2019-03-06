import copy
import json
import os
import re

from dateutil import parser
import pysam

from gdc_readgroups.util import get_readgroup_template, write_readgroups

from gdc_readgroups.exceptions import (
    NoReadGroupError,
    InvalidPlatformError,
    InvalidPlatformModelError,
    MissingReadgroupIdError,
    InvalidDatetimeError,
    NotABamError
)

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
    rgpl = readgroup_dict['PL'].lower()
    if 'illumina' in rgpl:
        platform = 'Illumina'
    elif 'solid' in rgpl:
        platform = 'SOLiD'
    elif '454' in rgpl:
        platform = 'LS454'
    elif all(x in rgpl for x in ('ion', 'torrent')):
        platform = 'Ion Torrent'
    elif all(x in rgpl for x in ('complete', 'genomics')):
        platform = 'Complete Genomics'
    elif all(x in rgpl for x in ('pac', 'bio')):
        platform = 'PacBio'
    elif 'other' in rgpl:
        platform = 'Other'
    elif rgpl in ('capillary', 'helicos', 'ont'): #in the SAM specification
        platform = 'Other'
    else:
        logger.error('The read group {0} has an unrecognized PL (platform) value'
                     ' of: {1}'.format(readgroup_dict['ID'], readgroup_dict['PL']))
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
    rgpm = (readgroup_dict['PM'].lower()
            .strip()
            .replace(' ', '')
            .replace('-', '')
            .replace('_', '')
            .replace('.', '')
            .replace(',', ''))
    if '454' in rgpm  and any(x in rgpm for x in ('gs', 'flx', 'titanium')):
        platform_model = '454 GS FLX Titanium'
    elif all(x in rgpm for x in ('solid', '2')):
        platform_model = 'AB SOLiD 2'
    elif all(x in rgpm for x in ('solid', '3')):
        platform_model = 'AB SOLiD 3'
    elif all(x in rgpm for x in ('solid', '4')):
        platform_model = 'AB SOLiD 4'
    elif all(x in rgpm for x in ('complete', 'genomics')):
        platform_model = 'Complete Genomics'
    elif (all(x in rgpm for x in ('illumina', 'hiseq', 'x')) and
          any(x in rgpm for x in ('10', 'ten'))):
        platform_model = 'Illumina HiSeq X Ten'
    elif (all(x in rgpm for x in ('illumina', 'hiseq', 'x')) and
          any(x in rgpm for x in ('5', 'five'))):
        platform_model = 'Illumina HiSeq X Five'
    elif all(x in rgpm for x in ('illumina', 'iix')):
        platform_model = 'Illumina Genome Analyzer IIx'
    elif all(x in rgpm for x in ('illumina', 'ii')):
        platform_model = 'Illumina Genome Analyzer II'
    elif all(x in rgpm for x in ('illumina', '2000')):
        platform_model = 'Illumina HiSeq 2000'
    elif all(x in rgpm for x in ('illumina', '2500')):
        platform_model = 'Illumina HiSeq 2500'
    elif all(x in rgpm for x in ('illumina', '4000')):
        platform_model = 'Illumina HiSeq 4000'
    elif all(x in rgpm for x in ('illumina', 'miseq')):
        platform_model = 'Illumina MiSeq'
    elif all(x in rgpm for x in ('ion', 'torrent', 'pgm')):
        platform_model = 'Ion Torrent PGM'
    elif all(x in rgpm for x in ('ion', 'torrent', 'proton')):
        platform_model = 'Ion Torrent Proton'
    elif 'pacbio' in rgpm:
        platform_model = 'PacBio RS'
    else:
        logger.error('The read group {0} has an unrecognized PM (platform model)'
                     ' value of: {1}'.format(readgroup_dict['ID'], readgroup_dict['PM']))
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
        rgdt = parser.parse(readgroup_dict['DT'])
    except (ValueError, TypeError) as err:
        logger.error('e: {}'.format(err))
        logger.error('The read group {0} has an unrecognized DT (datetime)'
                     ' value of: {1}'.format(readgroup_dict['ID'], readgroup_dict['DT']))
        raise InvalidDatetimeError
    return rgdt.isoformat()

def harmonize_readgroup(readgroup_dict, logger):
    if not 'ID' in readgroup_dict:
        logger.error('"ID" is missing from readgroup: {}'.format(readgroup_dict))
        raise MissingReadgroupIdError
    rgpl = get_platform(readgroup_dict, logger)
    rgpm = get_platform_model(readgroup_dict, logger)
    rgdt = get_datetime(readgroup_dict, logger)
    if rgpl:
        readgroup_dict['PL'] = rgpl
    if rgpm:
        readgroup_dict['PM'] = rgpm
    if rgdt:
        readgroup_dict['DT'] = rgdt
    return readgroup_dict

def get_readgroup_dict_list(bam_readgroup_dict_list, logger):
    rg_template = get_readgroup_template()
    output = list()
    for bam_readgroup_dict in bam_readgroup_dict_list:
        rgp = harmonize_readgroup(bam_readgroup_dict, logger)
        readgroup_meta = copy.deepcopy(rg_template)
        if rgp.get('SM'):
            readgroup_meta['aliquots']['submitter_id'] = rgp['SM']
        if rgp.get('DS'):
            readgroup_meta['experiment_name'] = rgp['DS']
        if rgp.get('LB'):
            readgroup_meta['library_name'] = rgp['LB']
        if rgp.get('PL'):
            readgroup_meta['platform'] = rgp['PL']
        if rgp.get('ID'):
            readgroup_meta['read_group_name'] = rgp['ID']
        if rgp.get('CN'):
            readgroup_meta['sequencing_center'] = rgp['CN']
        if rgp.get('SM') and rgp.get('ID'):
            readgroup_meta['submitter_id'] = rgp['SM']+'_'+rgp['ID']
        if rgp.get('PM'):
            readgroup_meta['instrument_model'] = rgp['PM']
        if rgp.get('DT'):
            readgroup_meta['sequencing_date'] = rgp['DT']

        platform_unit = rgp.get('PU', None)
        pu_dict = resolve_platform_unit(platform_unit)
        if pu_dict:
            if pu_dict.get('FB'):
                readgroup_meta['flow_cell_barcode'] = pu_dict['FB']
            if pu_dict.get('LN'):
                readgroup_meta['lane_number'] = pu_dict['LN']
            if pu_dict.get('MB'):
                readgroup_meta['multiplex_barcode'] = pu_dict['MB']

            #CHECK_MATCH
            if rgp.get('BC') and pu_dict and pu_dict.get('MB'):
                if rgp['BC'] != pu_dict['MB']:
                    logger.info('In Read Group {0}, the BC tag ({1}) does not match the third'
                                ' dotted part of the PU tag ({2})'.format(rgp.get('ID'),
                                                                          rgp['BC'],
                                                                          pu_dict['MB']))
        output.append(readgroup_meta)
    return output

def extract_readgroup(bam_path, output_format, logger):
    bam_file = os.path.basename(bam_path)
    bam_file_base, _ = os.path.splitext(bam_file)
    out_file = '.'.join([bam_file_base, output_format])
    with open(bam_path) as f_open:
        samfile = pysam.AlignmentFile(f_open, 'rb', check_header=True, check_sq=False)
        if not samfile.is_bam:
            logger.error("This program only runs on BAM files.")
            raise NotABamError
        samfile_header = samfile.header
        bam_readgroup_dict_list = samfile_header.get('RG')
        if not bam_readgroup_dict_list:
            logger.error('There are no readgroups in BAM: {}'.format(samfile.filename))
            raise NoReadGroupError
        output = get_readgroup_dict_list(bam_readgroup_dict_list, logger)
    write_readgroups(output, out_file, logger)
    return out_file
