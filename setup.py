#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name = 'bam_readgroup_to_gdc_json',
      author = 'Jeremiah H. Savage',
      author_email = 'jeremiahsavage@gmail.com',
      version = 0.9,
      description = 'From a BAM, convert each readgroup to a json object.',
      url = 'https://github.com/NCI-GDC/bam_readgroup_to_gdc_json/',
      license = 'Apache 2.0',
      packages = find_packages(),
      install_requires = [
          'pysam==0.15.2',
          'python-dateutil==2.8.0'
      ],
      classifiers = [
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
      ],
      entry_points={
          'console_scripts': ['bam_readgroup_to_gdc_json=bam_readgroup_to_gdc_json.__main__:main']
      }
)
