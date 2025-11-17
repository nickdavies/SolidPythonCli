#!/usr/bin/env python
from setuptools import setup

setup(
    name="solid_cli",
    version="2.0",
    description=(
        "Quick CLI toolchain builder for use with SolidPython to make "
        "it easier to build/test models"
    ),
    author="Nick Davies",
    author_email="git@nickdavies.com.au",
    url="https://github.com/nickdavies/SolidPythonCli",
    py_modules=["solid_cli"],
    install_requires=["solidpython2"],
)
