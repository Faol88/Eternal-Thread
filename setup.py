"""
setup.py
~~~~~~~~
Standard setuptools build script for eternal_memory_core.
"""

from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="eternal-memory-core",
    version="1.5.0",
    author="Faol88",
    description="3D Weaire-Phelan & Associative Spiderweb Vector Living Memory Core for AI Agents and LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Faol88/eternal-memory-core",
    packages=find_packages(include=["core", "core.*", "ownership", "ownership.*", "ui", "ui.*"]),
    python_requires=">=3.9",
    install_requires=[
        "chromadb>=0.4.22",
        "sentence-transformers>=2.2.2",
        "pyyaml>=6.0.1",
        "customtkinter>=5.2.0",
        "cryptography>=41.0.0",
        "requests>=2.31.0",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="ai memory rag llm 3d-spatial vector-database chromadb ollama agents",
)
