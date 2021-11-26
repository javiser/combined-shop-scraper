from setuptools import find_packages, setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="scraper",
    version="0.1.0",
    description="A simple combined shop scraper",
    license="MIT",
    long_description=long_description,
    author="javiser",
    author_email="javiser@users.noreply.github.com",
    url="https://github.com/javiser/combined-shop-scraper",
    packages=find_packages(exclude=["tests", ".github"]),
    install_requires=["bs4", "coloredlogs"],
    entry_points={"console_scripts": ["scraper = scraper.__main__:main"]},
)
