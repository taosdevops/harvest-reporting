from setuptools import find_packages, setup

setup(
    author="TAOS DevopsNow",
    name="harvestcli",
    description="harvestcli - Harvest cli utility for running reports",
    license=open("LICENSE").read(),
    long_description=open("README.md").read(),
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    version="0.1.0",
    url="https://github.com/",
    install_requires=[
        "Click==7.0",
        "colorama==0.4.1",
        "PyYAML==5.1.2",
        "requests==2.22.0",
    ],
    entry_points="""
        [console_scripts]
        harvestcli=hreporting.cli:main
    """,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNUGPLv3 License",
        "Operating System :: OS Independent",
    ],
)
