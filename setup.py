import sys

import setuptools

if sys.version_info < (3, 8):
    raise RuntimeError('bolsa requires Python 3.8+')

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='bolsa',
    version='0.0.1',
    author='Giovanni Cornachini',
    author_email='giovannicornachini@gmail.com',
    description=(
        'Biblioteca feita em python com o objetivo de facilitar o acesso a '
        'dados de seus investimentos na bolsa de valores(B3/CEI).'
    ),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/gicornachini/bolsa',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
 )
