#!/usr/bin/env python
from setuptools import setup

setup(
    name="OpenPySCADCli",
    version="1.0",
    description=(
        "Quick CLI wrapper for use with openpyscad to make it easier to build/models"
    ),
    author="Nick Davies",
    author_email="git@nickdavies.com.au",
    url="https://github.com/nickdavies/openpyscad-cli",
    py_modules=["openpyscad_cli"],
    install_requires=["openpyscad"],
)
