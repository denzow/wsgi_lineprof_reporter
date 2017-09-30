# coding: utf-8

from setuptools import setup, find_packages
from wlreporter import __VERSION__


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license_txt = f.read()

setup(
    name='wlreporter',
    version=__VERSION__,
    description='create report for wsgi_lineprof.',
    entry_points={
        "console_scripts": [
            "wlreporter = wlreporter.wlreporter:main"
        ]
    },
    long_description=readme,
    author='denzow',
    author_email='denzow@gmail.com',
    url='https://github.com/denzow/wsgi_lineprof_reporter',
    license=license_txt,
    packages=find_packages(exclude=('sample',))
)
