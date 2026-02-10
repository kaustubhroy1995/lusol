"""
PyLUSOL: Python interface to LUSOL sparse matrix factorization library

LUSOL maintains LU factors of square or rectangular sparse matrices.
This Python package provides a high-level interface to the LUSOL library.
"""

from .lusol import LUSOL

__version__ = '1.0.0'
__all__ = ['LUSOL']
