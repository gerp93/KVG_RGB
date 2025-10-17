"""
Setup script for KVG RGB Controller
"""
from setuptools import setup, find_packages
import os

# Read version from kvg_rgb/__init__.py
version = {}
with open(os.path.join("kvg_rgb", "__init__.py")) as f:
    exec(f.read(), version)

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kvg-rgb",
    version=version['__version__'],
    description="RGB device controller using OpenRGB with CLI and web UI support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="KVG",
    packages=find_packages(),
    include_package_data=True,  # Include non-Python files specified in MANIFEST.in
    package_data={
        'kvg_rgb': [
            'static/*.css',
            'static/*.js',
            'templates/*.html',
        ],
    },
    install_requires=[
        "openrgb-python>=0.2.15",
        "flask>=2.0.0",  # Required for web UI
    ],
    entry_points={
        'console_scripts': [
            'kvg-rgb=kvg_rgb.cli:main',
        ],
    },
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
