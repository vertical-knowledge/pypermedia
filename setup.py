from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path

__author__ = 'Alex Maskovyak'
__pkg_name__ = 'pypermedia'


here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'pypermedia', 'VERSION'), encoding='utf-8') as f:
    version = f.read().strip()

# run-time dependencies, listed here so that they can be shared with test requirements
install_requirements = [
    'requests>=2.3.0'
]

test_requirements = [
    'pytest'
] + install_requirements


# setuptool packaging info
setup(
    name=__pkg_name__,
    version=version,
    description='Python client for hypermedia APIs.',
    long_description=long_description,

    author=__author__,
    author_email='alex.maskovyak@vertical-knowledge.com',

    license='GPLv2',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        #   2 - Pre-Alpha, 3 - Alpha, 4 - Beta, 5 - Production/Stable
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ],

    keywords='client rest hypermedia http proxy siren api hateoas',

    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    install_requires=install_requirements,
    tests_require=test_requirements,

    package_data={
        'pypermedia': ['VERSION'],
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place model files outside of your packages.
    # see http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['model/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    # entry_points={
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },
)
