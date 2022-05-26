from setuptools import setup
from mats import __version__

# read the long description
with open('readme.md', 'r') as f:
    long_description = f.read()

# read the requirements.txt
with open('requirements.txt', 'r') as f:
    requirements = [s.strip() for s in f.readlines()]
    requirements = [r for r in requirements if r]

setup_attributes = {
    'name': 'mats',
    'version': __version__,
    'description': 'Manufacturing Automated Test System, a framework for building device testing quickly and consistently',
    'long_description': long_description,
    'long_description_content_type': 'text/markdown',
    'url': 'https://github.com/slightlynybbled/mats',
    'author': 'Jason R. Jones',
    'author_email': 'slightlynybbled@gmail.com',
    'license': 'MIT',
    'packages': ['mats'],
    'python_requires': '>=3.7.0',
    'install_requires': requirements,
    'classifiers': [
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    'zip_safe': False
}

setup(**setup_attributes)
