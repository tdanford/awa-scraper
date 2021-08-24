#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="awa-scraper",
    version="0.1.0",
    description="Scraper Utilities for AWA",
    url="https://www.github.com/tdanford/awa-scraper",
    package_dir={"": "src"},
    install_requires=["requests", "gspread", "beautifulsoup4", "tqdm"],
    tests_require=["pytest", "black", "pytest-black"],
)
