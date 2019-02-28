import pytest
import logging
import os

from bam_readgroup_to_gdc_json.main import validate_inputs, extract_readgroup_json

logging.basicConfig(
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d_%H:%M:%S_%Z'
)

logger = logging.getLogger("test")

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data') 

def test_validate_inputs_fail():
    fil = os.path.join(DATA_DIR, 'empty_rg_header_no_seq.sam')
    with pytest.raises(ValueError):
        validate_inputs(fil, logger)

def test_validate_inputs_pass():
    fil = os.path.join(DATA_DIR, 'empty_rg_header_no_seq.bam')
    res = validate_inputs(fil, logger)
    assert res is None

def test_extract_norg():
    fil = os.path.join(DATA_DIR, 'empty_rg_header_no_seq.sam')
    with pytest.raises(ValueError): 
        extract_readgroup_json(fil, logger)

    fil = os.path.join(DATA_DIR, 'no_rg_header.sam')
    with pytest.raises(ValueError): 
        extract_readgroup_json(fil, logger)

def test_extract_all_rg():
    fil = os.path.join(DATA_DIR, 'rg_header_all_rg_tags.sam')
    extract_readgroup_json(fil, logger)
    assert 0
