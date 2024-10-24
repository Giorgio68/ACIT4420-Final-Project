# pylint: disable=all

import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="ACIT4420 Final Project",
    version="0.1.0",
    author="Giorgio Salvemini",
    author_email="s351995@oslomet.no",
    description=("The produced module for the final project in the subject ACIT4420"),
    url="https://github.com/Giorgio68/ACIT4420-Final-Project",
    packages=["TarjanPlanner"],
    long_description=read("README.md"),
    test_suite="TarjanPlanner.tests",
    install_requires=[
        "pytest>=8.3.3",
        "geopy>=2.4.1",
        "networkx>=3.4.2",
        "matplotlib>=3.9.2",
    ],
)
