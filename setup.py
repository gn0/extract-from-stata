#!/usr/bin/env python
# coding: utf8

from setuptools import setup

setup(
    name='extract_from_stata',
    version='1.0',
    description=u'Extracting information from Stata regression tables, lincom tables, and one-way tabulations, and stacking them up in CSV or LaTeX output tables.',
    author=u'Gabor Nyeki',
    url='http://www.gabornyeki.com/',
    packages=['extract_from_stata',
              'extract_from_stata.model',
              'extract_from_stata.view'],
    install_requires=['argh'],
    provides=['extract_from_stata (1.0)'],
    entry_points={
        'console_scripts': [
            'extract_from_stata = extract_from_stata.controller:main',
        ],
    }
    )
