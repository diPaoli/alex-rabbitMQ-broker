# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))


# This call to setup() does all the work
setup(
    name="alex-rabbitMQ-broker",
    version="0.2.0",
    description="RabbitMQ Handler for Python - by diPaoliAlex",
    long_description="RabbitMQ Handler for Python - by diPaoliAlex",
    long_description_content_type="text/markdown",
    author="Alexandre Paulo",
    license="MIT License",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: Other/Proprietary :: diPaoliAlex",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent"
    ],
    packages=['broker'],
    include_package_data=True,
    install_requires=['pika','retry']
)
