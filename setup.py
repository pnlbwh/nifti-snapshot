from distutils.core import setup
import setuptools
import sys
from os.path import join

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='nifti_snapshot',
    version='v0.1.10',
    description='First release to test pypi',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='kcho',
    author_email='kevincho@bwh.harvard.edu',
    url='https://github.com/pnlbwh/nifti-snapshot',
    download_url='https://github.com/pnlbwh/nifti-snapshot/archive/refs/tags/nifti-snapshot.zip',
    keywords=['nifti', 'snapshot'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.7',
    install_requires=['matplotlib>=3.3.2',
                      'numpy>=1.19.2',
                      'scipy>=1.5.2',
                      'seaborn>=0.11.0',
                      'nibabel>=3.2.1'],
    data_files=[('/nifti_snapshot', ['enigma_download.sh'])],
    scripts=['scripts/nifti_snapshot']
)
