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
    author_email="",
    url="https://github.com/gerp93/KVG_RGB",
    license="AGPL-3.0-or-later",
    packages=find_packages(),
    include_package_data=True,  # Include non-Python files specified in MANIFEST.in
    package_data={
        'kvg_rgb': [
            'static/*.css',
            'static/*.js',
            'templates/*.html',
            'scripts/*.bat',
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
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: System :: Hardware",
        "Topic :: Utilities",
    "License :: OSI Approved :: GNU Affero General Public License v3",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    keywords="rgb openrgb lighting led controller cli web-ui hardware",
    project_urls={
        "Bug Reports": "https://github.com/gerp93/KVG_RGB/issues",
        "Source": "https://github.com/gerp93/KVG_RGB",
        "Documentation": "https://github.com/gerp93/KVG_RGB#readme",
    },
)
