"""
Setup configuration for BCI Artifact Rejection API
"""

import os
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() 
        for line in fh 
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="bci-artifact-rejection",
    version="2.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered EEG artifact rejection API for BCI applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/bci-artifact-rejection-api",
    packages=find_packages(include=["src", "src.*", "api", "api.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    include_package_data=True,
    zip_safe=False,
)
