from setuptools import find_packages, setup
import pathlib
import os

setup(
    author="TAOS DevopsNow",
    name="harvestcli",
    description="harvestcli - Harvest cli utility for running reports",
    # license=open("LICENSE").read(),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    version=open(os.path.join(".", "VERSION")).read().strip(),
    url="https://github.com/taosmountain/harvest-reporting",
    install_requires=[
        "dacite",
        "google-cloud-secret-manager",
        "google-cloud-storage",
        "python-harvest-apiv2",
        "pymsteams",
        "PyYAML",
        "sendgrid",
        "taosdevopsutils"
    ],
    extras_require={
        "docs": [
            "sphinx",
            "sphinx_rtd_theme"
        ],
        "tests": [
            "pytest",
            "pytest-cov",
            "vcrpy",
            "vcrpy-unittest",
            "pytest-vcr"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
