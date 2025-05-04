#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="i18n-updater-cn",
    version="1.0.0",
    author="CFPA Team",
    author_email="kressety@163.com",
    description="Minecraft模组汉化包更新器",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kressety/I18nUpdatePython",
    project_urls={
        "Bug Tracker": "https://github.com/kressety/I18nUpdatePython/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "i18n_updater_cn": ["*.json"],
    },
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "i18n-updater-cn=i18n_updater_cn.main:cli_main",
        ],
    },
)