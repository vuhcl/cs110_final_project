from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='cs110_finalproject_vu_quotientfilter',
    version='1.0aN',  # Required
    description='Final Project - CS110 Fall 2017',
    url='https://github.com/vuhcl/cs110_final_project',
    author='Vu H. Chu-Le',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],

    py_modules=["__init__.py"],
    install_requires=['mmh3', 'math', 'numpy'],
)
