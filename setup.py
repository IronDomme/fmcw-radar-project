from setuptools import setup, find_packages

setup(
    name="fmcw-radar-project",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
        'pytest',
    ],
    python_requires='>=3.8',
)
