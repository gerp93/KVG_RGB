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
    description="RGB device controller using OpenRGB with CLI and future GUI support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="KVG",
    packages=find_packages(),
    install_requires=[
        "openrgb-python>=0.2.15",
    ],
    entry_points={
        'console_scripts': [
            'kvg-rgb=kvg_rgb.cli:main',
        ],
        'gui_scripts': [
            # Future GUI entry point can go here
            # 'kvg-rgb-gui=kvg_rgb.gui:main',
        ],
    },
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
