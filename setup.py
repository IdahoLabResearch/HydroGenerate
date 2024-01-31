'''
Copyright 2021, Battelle Energy Alliance, LLC
'''

import os
import sys

from setuptools import setup, find_packages

with open(file="README.md", mode="r", encoding='utf-8') as readme_handle:
    long_description = readme_handle.read()

REQUIRED = [
    "requests>=2.26.0",
    "numpy>=1.19.2",
    "pandas>=1.1.5",
    "scipy>=1.1.0",
    "matplotlib>=2.1.0",
]

setup(
    name='HydroGenerate',
    # Read this as
    #   - MAJOR VERSION 1
    #   - MINOR VERSION 0
    #   - MAINTENANCE VERSION 0
    version='1.2.1',
    description='',
    long_description=long_description,
    url='https://github.com/IdahoLabResearch/HydroGenerate',
    author='Juan Gallego-Calderon',
    author_email='juan.gallegocalderon@inl.gov',
    license='BSD 3-Clause License',
    install_requires=REQUIRED,
    packages=find_packages(),
    python_requires='>=3.6'
)
