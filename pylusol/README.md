# PyLUSOL: Python Interface to LUSOL

PyLUSOL provides a Python interface to the LUSOL sparse matrix factorization library.

## Overview

LUSOL maintains LU factors of square or rectangular sparse matrices. This Python package provides a high-level, easy-to-use interface for:

- **LU factorization** of sparse matrices
- **Solving linear systems** with the factorization
- **Dynamic updates**: replacing columns/rows and adding/deleting columns/rows
- **Rank-1 modifications**
- **Matrix-vector multiplication** using stored factors

## Installation

### Prerequisites

1. **Build the LUSOL C library** first:
   ```bash
   make
   ```
   
   This creates:
   - `libclusol.so` on Linux
   - `libclusol.dylib` on macOS
   - `libclusol.dll` on Windows

2. **Python requirements**:
   - Python 3.6 or higher
   - NumPy >= 1.15.0
   - SciPy >= 1.0.0

### Install PyLUSOL

From the repository root:

```bash
pip install -e .
```

Or for development:

```bash
pip install -e .[dev]
```

## Quick Start

```python
import numpy as np
from pylusol import LUSOL

# Create a sparse matrix
A = np.array([
    [4, 1, 0, 0, 0],
    [1, 4, 1, 0, 0],
    [0, 1, 4, 1, 0],
    [0, 0, 1, 4, 1],
    [0, 0, 0, 1, 4]
], dtype=float)

# Factorize
lu = LUSOL(A)

# Solve Ax = b
b = np.array([1, 2, 3, 4, 5], dtype=float)
x = lu.solve(b)

print(f"Solution: {x}")
print(f"Residual: {np.linalg.norm(A @ x - b):.2e}")
```

## Usage Examples

### Using SciPy Sparse Matrices

```python
from scipy.sparse import csr_matrix
import numpy as np
from pylusol import LUSOL

# Create sparse matrix
n = 1000
A = csr_matrix((n, n))
# ... populate A ...

# Factorize and solve
lu = LUSOL(A)
b = np.ones(n)
x = lu.solve(b)
```

### Column Replacement

One of LUSOL's key features is efficient factorization updates:

```python
# Initial factorization
lu = LUSOL(A)

# Solve initial system
x1 = lu.solve(b)

# Replace column 2 with a new column
new_col = np.array([1, 2, 3], dtype=float)
lu.repcol(new_col, 2)  # Column index is 1-based

# Solve with updated matrix (much faster than re-factorizing)
x2 = lu.solve(b)
```

### Matrix-Vector Multiplication

```python
# Multiply by original matrix: y = A*x
y = lu.mulA(x, mode=5)

# Multiply by transpose: y = A'*x
yt = lu.mulA(x, mode=6)

# Lower-level operations:
# mode 1: y = L*x
# mode 2: y = L'*x  
# mode 3: y = U*x
# mode 4: y = U'*x
```

### Get Factorization Statistics

```python
stats = lu.get_stats()
print(f"Nonzeros in L and U: {stats['nelem']}")
print(f"Estimated rank: {stats['nrank']}")
print(f"Growth factor: {stats['growth']}")
```

## API Reference

### LUSOL Class

#### `__init__(A)`

Create a LUSOL factorization object.

- **Parameters:**
  - `A`: The matrix to factorize (numpy array or scipy sparse matrix)

#### `solve(b, mode=5)`

Solve a linear system using the LU factors.

- **Parameters:**
  - `b`: Right-hand side vector
  - `mode`: Solution mode (default: 5)
    - 1: solve L*v = v
    - 2: solve L'*v = v
    - 3: solve U*w = v
    - 4: solve U'*w = v
    - 5: solve A*x = b
    - 6: solve A'*x = b
- **Returns:** Solution vector

#### `mulA(x, mode=5)`

Multiply by the original matrix or its transpose.

- **Parameters:**
  - `x`: Input vector
  - `mode`: Multiplication mode
    - 1: compute y = L*x (L factor)
    - 2: compute y = L'*x (L transpose)
    - 3: compute y = U*x (U factor)
    - 4: compute y = U'*x (U transpose)
    - 5: compute y = A*x (default)
    - 6: compute y = A'*x (A transpose)
- **Returns:** Result vector

#### `repcol(v, jrep, mode1=2, mode2=2)`

Replace a column in the factorization.

- **Parameters:**
  - `v`: New column vector
  - `jrep`: Column index to replace (1-indexed)
  - `mode1`, `mode2`: Modes for update phases
- **Returns:** Status code (0 = success)

#### `get_stats()`

Get factorization statistics.

- **Returns:** Dictionary with keys:
  - `nelem`: Number of nonzeros in L and U
  - `nrank`: Estimated rank
  - `nsing`: Number of singularities
  - `growth`: Growth factor

## Examples

See the `examples/` directory for more detailed examples:

```bash
python examples/pylusol_example.py
```

## Module Structure

```
pylusol/
├── __init__.py      # Package initialization
├── lusol.py         # High-level LUSOL class
└── clusol.py        # Low-level ctypes bindings
```

## Performance Notes

- PyLUSOL uses **ctypes** to call the compiled C library, which provides near-native performance
- For best performance, ensure the LUSOL library is compiled with optimization flags (default in makefile)
- Sparse matrices are automatically converted to the appropriate format
- Column/row updates are much faster than re-factorization for large matrices

## Troubleshooting

### Library not found

If you get an error about `libclusol.so`, `libclusol.dylib`, or `libclusol.dll` not being found:

1. Make sure you built the C library: `make`
2. Check that the library exists in `src/` or `matlab/`
3. Set the library path manually:
   
   **Linux:**
   ```bash
   export LD_LIBRARY_PATH=/path/to/lusol/src:$LD_LIBRARY_PATH
   ```
   
   **macOS:**
   ```bash
   export DYLD_LIBRARY_PATH=/path/to/lusol/src:$DYLD_LIBRARY_PATH
   ```
   
   **Windows:**
   ```cmd
   set PATH=C:\path\to\lusol\src;%PATH%
   ```
   
   Or copy the DLL to your working directory:
   ```bash
   cp src/libclusol.dll .
   ```

### Windows-specific issues

**Problem: `libclusol.dll` not found or missing dependencies**

Windows requires additional DLL dependencies (from MinGW-w64) to be in your PATH:
- `libgfortran-*.dll`
- `libquadmath-*.dll`
- `libopenblas.dll` or `libblas.dll`
- `libgcc_s_seh-*.dll`

**Solution:** Ensure the MinGW-w64 `bin` directory is in your system PATH (e.g., `C:\msys64\mingw64\bin`). This makes all required DLLs accessible.

To verify:
```cmd
where libclusol.dll
where libopenblas.dll
```

### Import errors

Make sure NumPy and SciPy are installed:
```bash
pip install numpy scipy
```

## License

PyLUSOL follows the same license as LUSOL (MIT/BSD). See the LICENSE.md file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Authors

- **LUSOL Fortran code**: Michael Saunders (Stanford)
- **C interface**: Nick Henderson
- **Python interface**: Community contributors

## References

- [LUSOL website](http://web.stanford.edu/group/SOL/software/lusol/)
- [Original LUSOL paper](http://www.stanford.edu/group/SOL/software/lusol.html)
