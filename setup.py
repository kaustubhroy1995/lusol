#!/usr/bin/env python3
"""
Setup script for PyLUSOL

Python interface to LUSOL sparse matrix factorization library
"""

from setuptools import setup, find_packages
import os

# Read long description from README
long_description = """
PyLUSOL: Python Interface to LUSOL
===================================

PyLUSOL provides a Python interface to the LUSOL sparse matrix factorization library.

LUSOL maintains LU factors of square or rectangular sparse matrices and provides
efficient methods for:

- LU factorization of sparse matrices
- Solving linear systems with the factorization
- Dynamic updates: replacing columns/rows and adding/deleting columns/rows
- Rank-1 modifications

Installation
------------

Before installing PyLUSOL, you need to build the LUSOL C library:

```bash
make
```

Then install the Python package:

```bash
pip install -e .
```

Usage
-----

```python
import numpy as np
from pylusol import LUSOL

# Create a sparse matrix
A = np.array([[1, 2, 0], 
              [0, 3, 4], 
              [5, 0, 6]])

# Factorize
lu = LUSOL(A)

# Solve Ax = b
b = np.array([1, 2, 3])
x = lu.solve(b)

# Update a column
new_col = np.array([7, 8, 9])
lu.repcol(new_col, 1)  # Replace column 1 (1-indexed)

# Solve again with updated factorization
x_new = lu.solve(b)
```

Requirements
------------

- Python 3.6+
- NumPy
- SciPy
- LUSOL C library (libclusol.so or libclusol.dylib)
"""

setup(
    name='pylusol',
    version='1.0.0',
    description='Python interface to LUSOL sparse matrix factorization library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='LUSOL Contributors',
    author_email='',
    url='https://github.com/kaustubhroy1995/lusol',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'numpy>=1.15.0',
        'scipy>=1.0.0',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
    keywords='sparse matrix factorization linear algebra LU',
)
