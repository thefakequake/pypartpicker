from setuptools import setup

with open("README.md", "r", encoding="utf-8") as readme:
    long_description = readme.read()

setup(
    name="pypartpicker",
    version="1.9.2",
    description="A package that scrapes pcpartpicker.com and returns the results as objects.",
    packages=["pypartpicker"],
    url="https://github.com/thefakequake/pypartpicker",
    keywords=["pcpartpicker", "scraper", "list", "beautifulsoup", "pc", "parts"],
    install_requires=["bs4", "requests"],
    zip_safe=False,
    download_url="https://github.com/thefakequake/pypartpicker/archive/refs/tags/v1.9.2.tar.gz",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)
