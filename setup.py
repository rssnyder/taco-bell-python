import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="taco-bell-python",
    version="0.2.0",
    description="Order Taco Bell using Python!",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/rssnyder/taco-bell-python",
    author="Riley Snyder",
    author_email="rileysndr@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["tacobell"],
    include_package_data=True,
    install_requires=["requests"],
)
