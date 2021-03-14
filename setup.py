import sys

import setuptools

if sys.version_info < (3, 8):
    raise RuntimeError('bolsa requires Python 3.8+')

with open('README.md', 'r') as fh:
    long_description = fh.read()

install_requires = [
    'aiohttp>=3.6.2,<4.0.0',
    'cchardet>=2.1.6',
    'aiodns>=2.0.1',
    'beautifulsoup4>=4.9.2',
]


setuptools.setup(
    name='bolsa',
    version='2.0.3',
    packages=setuptools.find_packages(),
    python_requires='>=3.8.*',
    author='Giovanni Cornachini',
    author_email='giovannicornachini@gmail.com',
    description=(
        'Biblioteca feita em python com o objetivo de facilitar o acesso a '
        'dados de seus investimentos na bolsa de valores(B3/CEI).'
    ),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/gicornachini/bolsa',
    install_requires=install_requires,
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows'
    ],
)
