from setuptools import find_packages, setup


setup(
    name='httpbase',
    version="0.1.0",
    author='Ian Auld',
    author_email='imauld@gmail.com',
    description="Library for quickly making those simple HTTP clients we all end up writing all the time",
    packages=find_packages(),
    include_package_data=True,
    install_requires=['requests'],
    zip_safe=False,
)
