# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))


# This call to setup() does all the work
setup(
    name="pulsus-erik",
    version="0.2.0",
    description="RabbitMQ Handler for Python",
    long_description="RabbitMQ Handler for Python",
    long_description_content_type="text/markdown",
    author="Alexandre Santos",
    license="Pulsus",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: Other/Proprietary :: Pulsus",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
    ],
    packages=['rabbit_broker'],
    include_package_data=True,
    install_requires=['pika','retry']
)
