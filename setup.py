from setuptools import find_packages, setup

setup(
    author="TAOS DevopsNow",
    name="harvestcli",
    description="harvestcli - Harvest cli utility for running reports",
    # license=open("LICENSE").read(),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    version="0.1.1",
    url="https://github.com/taosmountain/harvest-reporting",
    install_requires=[
        "Click>=7.0",
        "colorama>=0.4",
        "PyYAML>=5.1",
        "requests>=2.22",
        "sendgrid>=6.2",
    ],
    entry_points="""
        [console_scripts]
        harvestcli=hreporting.cli:main
    """,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
