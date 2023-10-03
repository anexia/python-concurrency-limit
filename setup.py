import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as fh:
    readme = fh.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="concurrency-limit",
    version=os.getenv("PACKAGE_VERSION", "0.0.0").replace("refs/tags/", ""),
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    description="A library that implements a distributed concurrency limiting mechanism using Redis as a backend.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/anexia/python-concurrency-limit",
    author="Andreas Stocker",
    author_email="AStocker@anexia.com",
    install_requires=["redis>=4.0"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development",
    ],
)
