import util

from bam_readgroup_to_gdc_json import extract_readgroup

import argparse
import logging
import os
import unittest

import pysam

from bam_readgroup_to_gdc_json import __main__ as main
from bam_readgroup_to_gdc_json.exceptions import InvalidPlatformError

SAMFILE='rg_header_invalid_pl.sam'

class TestInvalidPl(unittest.TestCase):
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
        except InvalidPlatformError:
            pass
        else:
            self.logger.error('Input File\n\t{}\ndid not raise `InvalidPlatformError`'.format(self.bam))
            raise RuntimeError

if __name__ == "__main__":
    unittest.main()
