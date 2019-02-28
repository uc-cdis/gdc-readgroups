import util

from bam_readgroup_to_gdc_json import extract_readgroup

import argparse
import logging
import os
import unittest

import pysam

from bam_readgroup_to_gdc_json import main
from bam_readgroup_to_gdc_json.exceptions import MissingReadgroupIdError

SAMFILE='rg_header_no_id.sam'

class TestNoId(unittest.TestCase):
    def setUp(self):
        self.parser = argparse.ArgumentParser()
        self.parser.set_defaults(level=logging.DEBUG)
        self.args = self.parser.parse_args([])
        self.logger = main.setup_logging(self.args)
        current_dir = os.path.dirname(os.path.realpath(__file__))
        sam = os.path.join(current_dir, 'data', SAMFILE)
        self.bam = util.subprocess_make_bam(sam, self.logger)

    def tearDown(self):
        os.remove(self.bam)

    def test(self):
        try:
            self.testjson = extract_readgroup.extract_readgroup_json(self.bam, self.logger)
        except MissingReadgroupIdError:
            pass

if __name__ == "__main__":
    unittest.main()
