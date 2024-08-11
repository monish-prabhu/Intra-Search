from setuptools import setup, find_packages
from intra_search.config import SHORT_DESC


def read_requirements(file):
    with open(file) as f:
        return f.read().splitlines()


def read_file(file):
    with open(file) as f:
        return f.read()


requirements = read_requirements("./requirements.txt")
# long_description = read_file("README.md")

setup(
    name="intra-search",
    version="0.1.0",
    author="Monish Prabhu",
    author_email="monish.prabhu.official@gmail.com",
    # url = '',
    description=SHORT_DESC,
    # long_description_content_type = "text/markdown",
    # long_description = long_description,
    license="MIT license",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={"console_scripts": ["intra-search = intra_search.cli:cli"]},
    package_data={
        "intra_search": ["../ui/dist/**/*"],
    },
)
