'''
Copyright 2021, Battelle Energy Alliance, LLC
'''

import os
import sys

from setuptools import setup, find_packages

with open(file="README.md", mode="r", encoding='utf-8') as readme_handle:
    long_description = readme_handle.read()

REQUIRED = [
    "requests",
    "numpy",
    "pandas",
    "scipy",
    "matplotlib",
    "shapely"
]

setup(
    name='HydroGenerate',
    # Read this as
    #   - MAJOR VERSION 1
    #   - MINOR VERSION 0
    #   - MAINTENANCE VERSION 0
    version='1.3.0',
    description='',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/IdahoLabResearch/HydroGenerate',
    author='Juan Gallego-Calderon',
    author_email='juan.gallegocalderon@inl.gov',
    license='BSD 3-Clause License',
    install_requires=REQUIRED,
    packages=find_packages(),
    python_requires='>=3.8'
)
