import util

from bam_readgroup_to_gdc_json import extract_readgroup

import argparse
import logging
import os
import unittest

import pysam

from bam_readgroup_to_gdc_json import __main__ as main
from bam_readgroup_to_gdc_json.exceptions import NotABamError

SAMFILE='rg_header_all_rg_tags.sam'

class TestAllRgTags(unittest.TestCase):
    def setUp(self):
        self.parser = argparse.ArgumentParser()
        self.parser.set_defaults(level=logging.DEBUG)
        self.args = self.parser.parse_args([])
        self.logger = main.setup_logging(self.args)
        current_dir = os.path.dirname(os.path.realpath(__file__))
        sam = os.path.join(current_dir, 'data', SAMFILE)
        self.bam = sam

    def test(self):
        try:
            self.testjson = extract_readgroup.extract_readgroup(self.bam, 'json', self.logger)
        except NotABamError:
            pass
        else:
            self.logger.error('Input File\n\t{}\ndid not raise `NotABamError`'.format(self.bam))
            raise RuntimeError

if __name__ == "__main__":
    unittest.main()
