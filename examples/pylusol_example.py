#!/usr/bin/env python3
"""
Example usage of PyLUSOL

This script demonstrates basic usage of the PyLUSOL library for
sparse matrix factorization and solving linear systems.
"""

import numpy as np
from scipy.sparse import csr_matrix
from pylusol import LUSOL


def example_basic_solve():
    """Basic example: factorize and solve"""
    print("=" * 60)
    print("Example 1: Basic Factorization and Solve")
    print("=" * 60)
    
    # Create a simple sparse matrix
    A = np.array([
        [4, 1, 0, 0, 0],
        [1, 4, 1, 0, 0],
        [0, 1, 4, 1, 0],
        [0, 0, 1, 4, 1],
        [0, 0, 0, 1, 4]
    ], dtype=float)
    
    print("Matrix A:")
    print(A)
    
    # Create right-hand side
    b = np.array([1, 2, 3, 4, 5], dtype=float)
    print("\nRight-hand side b:")
    print(b)
    
    # Factorize
    print("\nFactorizing matrix...")
    lu = LUSOL(A)
    
    # Get statistics
    stats = lu.get_stats()
    print(f"Factorization stats:")
    print(f"  Number of nonzeros: {stats['nelem']}")
    print(f"  Estimated rank: {stats['nrank']}")
    
    # Solve Ax = b
    print("\nSolving Ax = b...")
    x = lu.solve(b)
    print("Solution x:")
    print(x)
    
    # Verify solution
    residual = np.linalg.norm(A @ x - b)
    print(f"\nResidual ||Ax - b||: {residual:.2e}")


def example_sparse_matrix():
    """Example with scipy sparse matrix"""
    print("\n" + "=" * 60)
    print("Example 2: Using SciPy Sparse Matrix")
    print("=" * 60)
    
    # Create a larger sparse matrix
    n = 10
    data = []
    row = []
    col = []
    
    # Tridiagonal matrix
    for i in range(n):
        # Diagonal
        data.append(4.0)
        row.append(i)
        col.append(i)
        
        # Upper diagonal
        if i < n - 1:
            data.append(-1.0)
            row.append(i)
            col.append(i + 1)
        
        # Lower diagonal
        if i > 0:
            data.append(-1.0)
            row.append(i)
            col.append(i - 1)
    
    A = csr_matrix((data, (row, col)), shape=(n, n))
    print(f"Created {n}x{n} tridiagonal matrix")
    print(f"Number of nonzeros: {A.nnz}")
    
    # Create right-hand side
    b = np.ones(n)
    
    # Factorize and solve
    print("\nFactorizing...")
    lu = LUSOL(A)
    
    print("Solving...")
    x = lu.solve(b)
    
    # Verify
    residual = np.linalg.norm(A @ x - b)
    print(f"Residual ||Ax - b||: {residual:.2e}")


if __name__ == '__main__':
    print("\nPyLUSOL Examples")
    print("=" * 60)
    
    try:
        example_basic_solve()
        example_sparse_matrix()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()
