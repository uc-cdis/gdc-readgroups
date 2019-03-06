import argparse
import json
import logging
import os
import unittest

import pysam

from gdc_readgroups import __main__ as main
from gdc_readgroups import extract_readgroup
from tests import util

SAMFILE='rg_header_only_id.sam'
EXPECTEDJSON = 'expected.rg_header_only_id.json'

class TestOnlyId(unittest.TestCase):
    def setUp(self):
        self.parser = argparse.ArgumentParser()
        self.parser.set_defaults(level=logging.DEBUG)
        self.args = self.parser.parse_args([])
        self.logger = main.setup_logging(self.args)
        current_dir = os.path.dirname(os.path.realpath(__file__))
        sam = os.path.join(current_dir, 'data', SAMFILE)
        expectedjson = os.path.join(current_dir, 'data', EXPECTEDJSON)
        with open(expectedjson, 'r') as f:
            self.expecteddata = json.load(f)
        self.bam = util.make_bam(sam)

    def tearDown(self):
        os.remove(self.bam)
        os.remove(self.testjson)

    def test(self):
        self.testjson = extract_readgroup.extract_readgroup(self.bam, 'json', self.logger)
        with open(self.testjson, 'r') as f:
            testdata = json.load(f)
        self.assertEqual(self.expecteddata, testdata)

if __name__ == "__main__":
    unittest.main()
