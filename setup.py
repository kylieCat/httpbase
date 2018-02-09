from setuptools import find_packages, setup
import sys


if sys.version_info < (3, 6):
    sys.exit('Sorry, Python < 3.6 is not supported')

setup(
    name='httpbase',
    version="0.1.1",
    author='Ian Auld',
    author_email='imauld@gmail.com',
    description="Library for quickly making those simple HTTP clients we all end up writing all the time",
    packages=find_packages(),
    include_package_data=True,
    install_requires=['requests'],
    zip_safe=False,
)
