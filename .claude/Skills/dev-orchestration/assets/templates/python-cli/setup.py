"""
Setup configuration for [PROJECT_NAME].
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="PROJECT_NAME",  # Replace with your project name
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Brief description of your project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/PROJECT_NAME",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        # Add your runtime dependencies here
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "PROJECT_NAME=src.cli:main",
        ],
    },
)
