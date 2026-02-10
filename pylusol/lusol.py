"""
High-level Python interface to LUSOL

This module provides a user-friendly object-oriented interface to LUSOL.
"""

import numpy as np
import ctypes
from scipy.sparse import coo_matrix, csr_matrix, issparse
from .clusol import _clusol


class LUSOL:
    """
    LUSOL: LU factorization for sparse matrices
    
    This class maintains LU factors of a square or rectangular sparse matrix
    and provides methods for solving linear systems and updating the factorization.
    
    Parameters
    ----------
    A : array_like or sparse matrix
        The matrix to factorize. Can be dense numpy array or scipy sparse matrix.
    
    Attributes
    ----------
    m : int
        Number of rows
    n : int
        Number of columns
    nelem : int
        Number of non-zero elements
    
    Examples
    --------
    >>> import numpy as np
    >>> from pylusol import LUSOL
    >>> A = np.array([[1, 2, 0], [0, 3, 4], [5, 0, 6]])
    >>> lu = LUSOL(A)
    >>> b = np.array([1, 2, 3])
    >>> x = lu.solve(b)
    """
    
    def __init__(self, A):
        """Initialize LUSOL with matrix A"""
        # Convert to sparse format if needed
        if not issparse(A):
            A = csr_matrix(A)
        
        # Convert to COO format for easier access
        A_coo = A.tocoo()
        
        # Store dimensions
        self.m = A_coo.shape[0]
        self.n = A_coo.shape[1]
        self.nelem = A_coo.nnz
        
        # Allocate arrays with enough space (factor of 3 for fill-in)
        self.lena = max(self.nelem * 3, 10000)
        
        # Initialize LUSOL parameters
        self.luparm = np.zeros(30, dtype=np.int64)
        self.parmlu = np.zeros(30, dtype=np.float64)
        
        # Set default parameters
        self._set_default_parameters()
        
        # Allocate data arrays
        self.a = np.zeros(self.lena, dtype=np.float64)
        self.indc = np.zeros(self.lena, dtype=np.int64)
        self.indr = np.zeros(self.lena, dtype=np.int64)
        
        # Permutation arrays
        self.p = np.zeros(self.m, dtype=np.int64)
        self.q = np.zeros(self.n, dtype=np.int64)
        
        # Length and location arrays
        self.lenc = np.zeros(self.n, dtype=np.int64)
        self.lenr = np.zeros(self.m, dtype=np.int64)
        self.locc = np.zeros(self.n, dtype=np.int64)
        self.locr = np.zeros(self.m, dtype=np.int64)
        
        # Location arrays for permutations
        self.iploc = np.zeros(self.m, dtype=np.int64)
        self.iqloc = np.zeros(self.n, dtype=np.int64)
        self.ipinv = np.zeros(self.m, dtype=np.int64)
        self.iqinv = np.zeros(self.n, dtype=np.int64)
        
        # Work array
        self.w = np.zeros(self.n, dtype=np.float64)
        
        # Copy matrix data into LUSOL arrays (1-indexed for Fortran)
        # NOTE: LUSOL expects row indices in indc and column indices in indr!
        for i in range(self.nelem):
            self.a[i] = A_coo.data[i]
            self.indc[i] = A_coo.row[i] + 1  # Row index in indc (1-indexed)
            self.indr[i] = A_coo.col[i] + 1  # Column index in indr (1-indexed)
        
        # Perform factorization
        self._factorize()
    
    def _set_default_parameters(self):
        """Set default LUSOL parameters"""
        # luparm parameters (0-indexed in Python, 1-indexed in Fortran docs)
        self.luparm[0] = 0   # nout: output unit (0 = no output)
        self.luparm[1] = 10  # lprint: print level
        self.luparm[2] = 5   # maxcol: max columns in Markowitz search
        self.luparm[5] = 0   # pivot: pivoting method (0=TPP, 1=TRP, 2=TCP, 3=TSP)
        self.luparm[7] = 1   # keepLU: keep = 1 to save LU factors
        
        # parmlu parameters
        self.parmlu[0] = 10.0  # Lmax1: max multiplier in initial Lmax
        self.parmlu[1] = 10.0  # Lmax2: max multiplier in later Lmax
        self.parmlu[2] = 1e-13  # small: absolute pivot tolerance (eps^0.8)
        self.parmlu[3] = 1e-11  # Utol1: abs tol for flagging small diagonals (eps^0.67)
        self.parmlu[4] = 1e-11  # Utol2: rel tol for flagging small diagonals (eps^0.67)
        self.parmlu[5] = 3.0   # Uspace: Space factor for U
        self.parmlu[6] = 0.3   # dens1: density for threshold pivoting
        self.parmlu[7] = 0.5   # dens2: density for dense LU
    
    def _factorize(self):
        """Perform LU factorization"""
        inform = ctypes.c_int64(0)
        
        _clusol.clu1fac(
            ctypes.byref(ctypes.c_int64(self.m)),
            ctypes.byref(ctypes.c_int64(self.n)),
            ctypes.byref(ctypes.c_int64(self.nelem)),
            ctypes.byref(ctypes.c_int64(self.lena)),
            self.luparm.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.parmlu.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            self.a.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            self.indc.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.indr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.p.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.q.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.lenc.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.lenr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.locc.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.locr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.iploc.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.iqloc.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.ipinv.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.iqinv.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.w.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            ctypes.byref(inform)
        )
        
        if inform.value != 0:
            raise RuntimeError(f"LU factorization failed with inform = {inform.value}")
    
    def solve(self, b, mode=5):
        """
        Solve a linear system using the LU factors
        
        Parameters
        ----------
        b : array_like
            Right-hand side vector
        mode : int, optional
            Solution mode:
            - 1: solve L*v = v
            - 2: solve L'*v = v
            - 3: solve U*w = v
            - 4: solve U'*w = v
            - 5: solve A*x = b (default)
            - 6: solve A'*x = b
        
        Returns
        -------
        x : ndarray
            Solution vector
        """
        b = np.asarray(b, dtype=np.float64)
        if b.shape[0] != self.m:
            raise ValueError(f"RHS vector size {b.shape[0]} does not match matrix rows {self.m}")
        
        v = b.copy()
        w = np.zeros(self.n, dtype=np.float64)
        inform = ctypes.c_int64(0)
        
        _clusol.clu6sol(
            ctypes.byref(ctypes.c_int64(mode)),
            ctypes.byref(ctypes.c_int64(self.m)),
            ctypes.byref(ctypes.c_int64(self.n)),
            v.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            w.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            ctypes.byref(ctypes.c_int64(self.lena)),
            self.luparm.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.parmlu.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            self.a.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            self.indc.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.indr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.p.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.q.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.lenc.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.lenr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.locc.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.locr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            ctypes.byref(inform)
        )
        
        if inform.value != 0:
            raise RuntimeError(f"Solve failed with inform = {inform.value}")
        
        return w if mode in [5, 6] else v
    
    def mulA(self, x, mode=1):
        """
        Multiply by the original matrix or its transpose
        
        Parameters
        ----------
        x : array_like
            Input vector
        mode : int, optional
            - 1: compute w = A*x (default)
            - 2: compute w = A'*x
        
        Returns
        -------
        w : ndarray
            Result vector
        """
        x = np.asarray(x, dtype=np.float64)
        v = x.copy()
        w = np.zeros(self.m if mode == 1 else self.n, dtype=np.float64)
        
        _clusol.clu6mul(
            ctypes.byref(ctypes.c_int64(mode)),
            ctypes.byref(ctypes.c_int64(self.m)),
            ctypes.byref(ctypes.c_int64(self.n)),
            v.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            w.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            ctypes.byref(ctypes.c_int64(self.lena)),
            self.luparm.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.parmlu.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            self.a.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            self.indc.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.indr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.p.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.q.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.lenc.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.lenr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.locc.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.locr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64))
        )
        
        return w
    
    def repcol(self, v, jrep, mode1=2, mode2=2):
        """
        Replace a column in the factorization
        
        Parameters
        ----------
        v : array_like
            New column vector
        jrep : int
            Column index to replace (1-indexed)
        mode1 : int, optional
            Mode for first phase (default: 2)
        mode2 : int, optional
            Mode for second phase (default: 2)
        
        Returns
        -------
        inform : int
            Status code
        """
        v = np.asarray(v, dtype=np.float64)
        w = np.zeros(self.m, dtype=np.float64)
        inform = ctypes.c_int64(0)
        diag = ctypes.c_double(0.0)
        vnorm = ctypes.c_double(0.0)
        
        _clusol.clu8rpc(
            ctypes.byref(ctypes.c_int64(mode1)),
            ctypes.byref(ctypes.c_int64(mode2)),
            ctypes.byref(ctypes.c_int64(self.m)),
            ctypes.byref(ctypes.c_int64(self.n)),
            ctypes.byref(ctypes.c_int64(jrep)),
            v.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            w.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            ctypes.byref(ctypes.c_int64(self.lena)),
            self.luparm.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.parmlu.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            self.a.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            self.indc.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.indr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.p.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.q.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.lenc.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.lenr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.locc.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            self.locr.ctypes.data_as(ctypes.POINTER(ctypes.c_int64)),
            ctypes.byref(inform),
            ctypes.byref(diag),
            ctypes.byref(vnorm)
        )
        
        return inform.value
    
    def get_stats(self):
        """
        Get factorization statistics
        
        Returns
        -------
        stats : dict
            Dictionary containing factorization statistics
        """
        return {
            'nelem': int(self.luparm[11]),  # Number of nonzeros in L and U
            'nrank': int(self.luparm[15]),  # Estimated rank
            'nsing': int(self.luparm[10]),  # Number of singularities
            'growth': float(self.parmlu[15]),  # Growth factor
        }
