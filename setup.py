"""Packaging settings."""
from setuptools import find_packages, setup

from osmox import __version__

# from typing_extensions import Required

with open("requirements.txt") as f:
    required = [line.rstrip('\n') for line in f]

setup(
    name="osmox",
    version=__version__,
    description="A command line tool for processing osmfs into facility locations.",
    packages=find_packages(),
    install_requires=required,
    python_requires='==3.7.*',
    entry_points={"console_scripts": ["osmox = osmox.main:osmox"]},
)
