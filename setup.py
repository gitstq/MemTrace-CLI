"""Setup script for MemTrace-CLI."""
from setuptools import find_packages, setup

setup(
    name="memtrace-cli",
    version="0.1.0",
    description="MemTrace-CLI — Lightweight Terminal AI Agent Shared Memory Engine",
    long_description=__doc__,
    long_description_content_type="text/markdown",
    author="MemTrace Team",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    entry_points={
        "console_scripts": [
            "memtrace=memtrace.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    keywords="ai agent memory cli session tracking",
)