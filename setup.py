#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name = 'bam_readgroup_to_gdc_json',
      packages = find_packages(),
      install_requires = [
          'pysam==0.15.2',
          'python-dateutil==2.8.0'
      ],
      entry_points={
          'console_scripts': ['bam_readgroup_to_gdc_json=bam_readgroup_to_gdc_json.__main__:main']
      }
)
