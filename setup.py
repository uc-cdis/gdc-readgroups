#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name = 'gdc_readgroups',
      packages = find_packages(),
      package_data={
          "gdc_readgroups": [
              "readgroup_template.json"
              ]
          },
      install_requires = [
          'pysam==0.15.2',
          'python-dateutil==2.8.0'
      ],
      entry_points={
          'console_scripts': ['gdc-readgroups=gdc_readgroups.__main__:main']
      }
)
