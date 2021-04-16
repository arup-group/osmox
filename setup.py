"""Packaging settings."""
import os
from setuptools import find_packages, setup
# from typing_extensions import Required

from osmox import __version__

with open("requirements.txt") as f:
    required = [line.rstrip('\n') for line in f]

setup(
    name="osmox",
    version=__version__,
    description="A command line tool for processing osmfs into facility locations.",
    packages=find_packages(),
    install_requires=required,
    entry_points={"console_scripts": ["osmox = osmox.main:osmox"]},
)
