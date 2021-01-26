"""Packaging settings."""

from setuptools import find_packages, setup

from osmox import __version__


setup(
    name="osmox",
    version=__version__,
    description="A command line tool for processing osmfs into facility locations.",
    packages=find_packages(),
    install_requires=[
        "pandas==0.23.4",
        "osmium==2.15.3",
        "pytest==3.7.1",
        "Shapely==1.6.4.post2",
        "setuptools==42.0.1",
        "Click==7.0",
        "geopandas==0.7.0",
        "Rtree==0.9.3"
    ],
    entry_points={"console_scripts": ["osmox = osmox.main:osmox"]},
)
