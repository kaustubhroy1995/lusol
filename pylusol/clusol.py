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
    """Find the LUSOL shared library.

    On macOS, if no pre-compiled dylib is found the function will
    attempt to build one from source by running ``make`` in the
    repository root.
    """
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
    
    # Search paths for the library
    pkg_dir = os.path.dirname(__file__)
    repo_root = os.path.normpath(os.path.join(pkg_dir, '..'))
    search_paths = [
        # Pre-compiled library bundled with the package
        os.path.join(pkg_dir, 'lib'),
        # Directory relative to this file (for development builds)
        os.path.join(repo_root, 'src'),
        os.path.join(repo_root, 'matlab'),
        # System paths
        '/usr/local/lib',
        '/usr/lib',
    ]
    
    for path in search_paths:
        lib_path = os.path.join(path, lib_name)
        if os.path.exists(lib_path):
            return lib_path

    # On macOS, attempt to build the library from source automatically
    if system == 'Darwin':
        lib_path = _build_library_macos(repo_root, pkg_dir)
        if lib_path is not None:
            return lib_path

    # If not found, try to load from system path
    return lib_name


def _build_library_macos(repo_root, pkg_dir):
    """Try to build libclusol.dylib from source on macOS.

    Returns the path to the built library on success, or ``None``.
    """
    import shutil
    import subprocess

    makefile = os.path.join(repo_root, 'makefile')
    if not os.path.exists(makefile):
        return None

    print("libclusol.dylib not found – attempting to build from source …")
    try:
        subprocess.check_call(['make', 'clean'], cwd=repo_root)
        subprocess.check_call(['make'], cwd=repo_root)
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"Warning: automatic build failed: {exc}\n"
              "Please run 'make' manually in the repository root.")
        return None

    src_lib = os.path.join(repo_root, 'src', 'libclusol.dylib')
    if not os.path.exists(src_lib):
        return None

    # Copy built library into the package lib directory for future use
    lib_dir = os.path.join(pkg_dir, 'lib')
    os.makedirs(lib_dir, exist_ok=True)
    dest = os.path.join(lib_dir, 'libclusol.dylib')
    shutil.copy2(src_lib, dest)
    return dest


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
