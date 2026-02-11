"""
Low-level ctypes interface to the LUSOL C library (clusol)

This module provides direct Python bindings to the C interface of LUSOL.
"""

import ctypes
import os
import platform
import numpy as np
from numpy.ctypeslib import ndpointer


def _find_library():
    """Find the LUSOL shared library"""
    # Determine library name based on platform
    system = platform.system()
    if system == 'Darwin':
        lib_name = 'libclusol.dylib'
    elif system == 'Linux':
        lib_name = 'libclusol.so'
    elif system == 'Windows':
        lib_name = 'libclusol.dll'
    else:
        raise OSError(f"Unsupported platform: {system}")
    
    # Build search paths for the library
    pkg_dir = os.path.dirname(__file__)
    search_paths = []

    # On macOS, check architecture-specific subdirectory first
    if system == 'Darwin':
        arch = platform.machine()  # e.g. 'arm64', 'x86_64'
        search_paths.append(
            os.path.join(pkg_dir, 'lib', f'darwin_{arch}'))

    search_paths += [
        # Pre-compiled library bundled with the package
        os.path.join(pkg_dir, 'lib'),
        # Directory relative to this file (for development builds)
        os.path.join(pkg_dir, '..', 'src'),
        os.path.join(pkg_dir, '..', 'matlab'),
        # System paths
        '/usr/local/lib',
        '/usr/lib',
    ]
    
    for path in search_paths:
        lib_path = os.path.join(path, lib_name)
        if os.path.exists(lib_path):
            return lib_path
    
    # If not found, try to load from system path
    return lib_name


# Load the LUSOL C library
_lib_path = _find_library()
_clusol = ctypes.CDLL(_lib_path)


# Define ctypes for int64_t* and double*
c_int64_p = ctypes.POINTER(ctypes.c_int64)
c_double_p = ctypes.POINTER(ctypes.c_double)


# clu1fac: LU factorization
_clusol.clu1fac.argtypes = [
    c_int64_p,  # m
    c_int64_p,  # n
    c_int64_p,  # nelem
    c_int64_p,  # lena
    c_int64_p,  # luparm
    c_double_p, # parmlu
    c_double_p, # a
    c_int64_p,  # indc
    c_int64_p,  # indr
    c_int64_p,  # p
    c_int64_p,  # q
    c_int64_p,  # lenc
    c_int64_p,  # lenr
    c_int64_p,  # locc
    c_int64_p,  # locr
    c_int64_p,  # iploc
    c_int64_p,  # iqloc
    c_int64_p,  # ipinv
    c_int64_p,  # iqinv
    c_double_p, # w
    c_int64_p,  # inform
]
_clusol.clu1fac.restype = None


# clu6sol: Solve with LU factors
_clusol.clu6sol.argtypes = [
    c_int64_p,  # mode
    c_int64_p,  # m
    c_int64_p,  # n
    c_double_p, # v
    c_double_p, # w
    c_int64_p,  # lena
    c_int64_p,  # luparm
    c_double_p, # parmlu
    c_double_p, # a
    c_int64_p,  # indc
    c_int64_p,  # indr
    c_int64_p,  # p
    c_int64_p,  # q
    c_int64_p,  # lenc
    c_int64_p,  # lenr
    c_int64_p,  # locc
    c_int64_p,  # locr
    c_int64_p,  # inform
]
_clusol.clu6sol.restype = None


# clu8rpc: Replace column
_clusol.clu8rpc.argtypes = [
    c_int64_p,  # mode1
    c_int64_p,  # mode2
    c_int64_p,  # m
    c_int64_p,  # n
    c_int64_p,  # jrep
    c_double_p, # v
    c_double_p, # w
    c_int64_p,  # lena
    c_int64_p,  # luparm
    c_double_p, # parmlu
    c_double_p, # a
    c_int64_p,  # indc
    c_int64_p,  # indr
    c_int64_p,  # p
    c_int64_p,  # q
    c_int64_p,  # lenc
    c_int64_p,  # lenr
    c_int64_p,  # locc
    c_int64_p,  # locr
    c_int64_p,  # inform
    c_double_p, # diag
    c_double_p, # vnorm
]
_clusol.clu8rpc.restype = None


# clu6mul: Multiply with LU factors
_clusol.clu6mul.argtypes = [
    c_int64_p,  # mode
    c_int64_p,  # m
    c_int64_p,  # n
    c_double_p, # v
    c_double_p, # w
    c_int64_p,  # lena
    c_int64_p,  # luparm
    c_double_p, # parmlu
    c_double_p, # a
    c_int64_p,  # indc
    c_int64_p,  # indr
    c_int64_p,  # p
    c_int64_p,  # q
    c_int64_p,  # lenc
    c_int64_p,  # lenr
    c_int64_p,  # locc
    c_int64_p,  # locr
]
_clusol.clu6mul.restype = None


# clu8adc: Add column
_clusol.clu8adc.argtypes = [
    c_int64_p,  # mode
    c_int64_p,  # m
    c_int64_p,  # n
    c_double_p, # v
    c_double_p, # w
    c_int64_p,  # lena
    c_int64_p,  # luparm
    c_double_p, # parmlu
    c_double_p, # a
    c_int64_p,  # indc
    c_int64_p,  # indr
    c_int64_p,  # p
    c_int64_p,  # q
    c_int64_p,  # lenc
    c_int64_p,  # lenr
    c_int64_p,  # locc
    c_int64_p,  # locr
    c_int64_p,  # inform
    c_double_p, # diag
    c_double_p, # vnorm
]
_clusol.clu8adc.restype = None


# clu8adr: Add row
_clusol.clu8adr.argtypes = [
    c_int64_p,  # m
    c_int64_p,  # n
    c_double_p, # w
    c_int64_p,  # lena
    c_int64_p,  # luparm
    c_double_p, # parmlu
    c_double_p, # a
    c_int64_p,  # indc
    c_int64_p,  # indr
    c_int64_p,  # p
    c_int64_p,  # q
    c_int64_p,  # lenc
    c_int64_p,  # lenr
    c_int64_p,  # locc
    c_int64_p,  # locr
    c_int64_p,  # inform
    c_double_p, # diag
]
_clusol.clu8adr.restype = None


# clu8dlc: Delete column
_clusol.clu8dlc.argtypes = [
    c_int64_p,  # m
    c_int64_p,  # n
    c_int64_p,  # jdel
    c_int64_p,  # lena
    c_int64_p,  # luparm
    c_double_p, # parmlu
    c_double_p, # a
    c_int64_p,  # indc
    c_int64_p,  # indr
    c_int64_p,  # p
    c_int64_p,  # q
    c_int64_p,  # lenc
    c_int64_p,  # lenr
    c_int64_p,  # locc
    c_int64_p,  # locr
    c_int64_p,  # inform
]
_clusol.clu8dlc.restype = None


# clu8dlr: Delete row
_clusol.clu8dlr.argtypes = [
    c_int64_p,  # mode
    c_int64_p,  # m
    c_int64_p,  # n
    c_int64_p,  # idel
    c_double_p, # v
    c_double_p, # w
    c_int64_p,  # lena
    c_int64_p,  # luparm
    c_double_p, # parmlu
    c_double_p, # a
    c_int64_p,  # indc
    c_int64_p,  # indr
    c_int64_p,  # p
    c_int64_p,  # q
    c_int64_p,  # lenc
    c_int64_p,  # lenr
    c_int64_p,  # locc
    c_int64_p,  # locr
    c_int64_p,  # inform
]
_clusol.clu8dlr.restype = None


# clu8mod: Rank-1 modification
_clusol.clu8mod.argtypes = [
    c_int64_p,  # mode
    c_int64_p,  # m
    c_int64_p,  # n
    c_double_p, # beta
    c_double_p, # v
    c_double_p, # w
    c_int64_p,  # lena
    c_int64_p,  # luparm
    c_double_p, # parmlu
    c_double_p, # a
    c_int64_p,  # indc
    c_int64_p,  # indr
    c_int64_p,  # p
    c_int64_p,  # q
    c_int64_p,  # lenc
    c_int64_p,  # lenr
    c_int64_p,  # locc
    c_int64_p,  # locr
    c_int64_p,  # inform
]
_clusol.clu8mod.restype = None


# clu8rpr: Replace row
_clusol.clu8rpr.argtypes = [
    c_int64_p,  # mode1
    c_int64_p,  # mode2
    c_int64_p,  # m
    c_int64_p,  # n
    c_int64_p,  # irep
    c_double_p, # v
    c_double_p, # w
    c_double_p, # wnew
    c_int64_p,  # lena
    c_int64_p,  # luparm
    c_double_p, # parmlu
    c_double_p, # a
    c_int64_p,  # indc
    c_int64_p,  # indr
    c_int64_p,  # p
    c_int64_p,  # q
    c_int64_p,  # lenc
    c_int64_p,  # lenr
    c_int64_p,  # locc
    c_int64_p,  # locr
    c_int64_p,  # inform
]
_clusol.clu8rpr.restype = None


# Export the library and functions
__all__ = ['_clusol']
