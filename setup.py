#!/usr/bin/env python3
"""
Setup script for PyLUSOL

Python interface to LUSOL sparse matrix factorization library
"""

from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
import os
import platform
import shutil
import subprocess
import sys


def _build_libclusol_macos(base_dir):
    """Build libclusol.dylib from source on macOS and copy to pylusol/lib/.

    This is invoked automatically during installation on macOS when a
    pre-compiled dylib for the current architecture is not already bundled.
    """
    lib_dir = os.path.join(base_dir, 'pylusol', 'lib')
    src_lib = os.path.join(base_dir, 'src', 'libclusol.dylib')

    print("Building libclusol.dylib from source ...")
    try:
        subprocess.check_call(['make', 'clean'], cwd=base_dir)
        subprocess.check_call(['make'], cwd=base_dir)
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(
            f"Warning: failed to build libclusol.dylib: {exc}\n"
            "You may need to install build dependencies "
            "(Xcode command-line tools, gfortran via Homebrew) "
            "and run 'make' manually.",
            file=sys.stderr,
        )
        return

    if os.path.exists(src_lib):
        os.makedirs(lib_dir, exist_ok=True)
        dest = os.path.join(lib_dir, 'libclusol.dylib')
        shutil.copy2(src_lib, dest)
        print(f"Copied libclusol.dylib to {dest}")
    else:
        print(
            "Warning: make succeeded but libclusol.dylib was not found in src/.",
            file=sys.stderr,
        )


class BuildPyWithMacOSLib(build_py):
    """Custom build_py that builds libclusol.dylib on macOS if needed."""

    def run(self):
        if platform.system() == 'Darwin':
            base_dir = os.path.dirname(os.path.abspath(__file__))
            dylib_path = os.path.join(base_dir, 'pylusol', 'lib', 'libclusol.dylib')
            if not os.path.exists(dylib_path):
                _build_libclusol_macos(base_dir)
        super().run()


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

Pre-compiled shared libraries for Linux (x86_64), Windows (x86_64), and
macOS (Apple Silicon arm64) are included. Simply install:

```bash
pip install -e .
```

On macOS, if a pre-compiled library is not bundled for your architecture, the
setup script will attempt to build it from source automatically (requires
Xcode command-line tools and gfortran via Homebrew).

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
- LUSOL C library (libclusol.so, libclusol.dylib, or libclusol.dll)
  Pre-compiled libraries for Linux (x86_64), Windows (x86_64), and
  macOS (Apple Silicon arm64) are included.
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
    package_data={
        'pylusol': ['lib/*.so', 'lib/*.dylib', 'lib/*.dll'],
    },
    cmdclass={
        'build_py': BuildPyWithMacOSLib,
    },
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
