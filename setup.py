from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
   name='scraper',
   version='0.1.0',
   description='A simple combined shop scraper',
   license="MIT",
   long_description=long_description,
   author='javiser',
   author_email='javiser@users.noreply.github.com',
   url="https://github.com/javiser/combined-shop-scraper",
   packages=['scraper'],
   install_requires=['bs4', 'coloredlogs'],
)