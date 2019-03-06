import argparse
import logging
import os
import unittest

import pysam

from gdc_readgroups import __main__ as main
from gdc_readgroups import extract_readgroup
from gdc_readgroups.exceptions import NoReadGroupError
from tests import util

SAMFILE='empty_rg_header_no_seq.sam'

class TestNoRgNoSq(unittest.TestCase):
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
            self.testjson = extract_readgroup.extract_readgroup(self.bam, 'json', self.logger)
        except NoReadGroupError:
            pass
        else:
            self.logger.error('Input File\n\t{}\ndid not raise `NoReadGroupError`'.format(self.bam))
            raise RuntimeError

if __name__ == "__main__":
    unittest.main()
