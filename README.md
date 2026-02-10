## LUSOL

[LUSOL][LUSOL] maintains LU factors of a square or rectangular sparse matrix.

This repository provides [LUSOL][LUSOL] source code, a Matlab interface, and **Python bindings**.

The code is distributed under the terms of the MIT License or the BSD License.

  [LUSOL]: http://web.stanford.edu/group/SOL/software/lusol/

## Python Interface (PyLUSOL)

PyLUSOL provides a Python interface to LUSOL with support for:

- LU factorization of sparse matrices
- Solving linear systems (A*x=b, A'*x=b)
- Column/row replacement for efficient updates
- Matrix-vector multiplication with stored factors
- Full NumPy and SciPy sparse matrix support

### Quick Start (Python)

```python
import numpy as np
from pylusol import LUSOL

# Factorize and solve
A = np.array([[4, 1, 0], [1, 4, 1], [0, 1, 4]], dtype=float)
b = np.array([1, 2, 3], dtype=float)

lu = LUSOL(A)
x = lu.solve(b)  # Solve A*x = b
```

### Python Installation

1. Build the C library:
   ```bash
   make
   ```

2. Install Python package:
   ```bash
   pip install -e .
   ```

See [pylusol/README.md](pylusol/README.md) for detailed Python documentation and [examples/pylusol_example.py](examples/pylusol_example.py) for usage examples.

## Contents

* `gen/`: code generation scripts and specification files
* `matlab/`: Matlab interface code
* `src/`: LUSOL Fortran code
* `LICENSE`: [Common Public License][CPL]
* `makefile`: GNU Make file to build interface

## Download and install

Pre-built downloads are available on the Github [release][RELEASE] page.

Installation simply requires adding the `matlab` subdirectory to your Matlab
path.  This may be done with Matlab's [`addpath`][ADDPATH] function.

If the interface has not been built, please follow the directions below.

  [RELEASE]: https://github.com/nwh/lusol/releases
  [ADDPATH]: http://www.mathworks.com/help/matlab/ref/addpath.html

## Basic usage

In Matlab:

```
% get L and U factors
[L U P Q] = lusol(A);
```

See `>>> help lusol`.

## Advanced usage

In Matlab:

```
% create lusol object
mylu = lusol_obj(A);

% solve with lusol object (ie x = A\b)
x = mylu.solveA(b);

% update factorization to replace a column
mylu.repcol(v,1);

% solve again with updated factorization
x1 = mylu.solveA(b);
```

See `>>> help lusol_obj`.

## Build

### Environment

The build environments as of 2016-01-26 are:

- Fedora 21 & Matlab 2013b
- Mac OS X 10.11 & Matlab 2015b
- Windows 10 with MSYS2/MinGW-w64

Building the LUSOL interface in other environments may require modification of
`makefile` and `matlab/lusol_build.m`.

### Requirements

Linux:

* `make`
* `gcc`
* `gfortran`
* Matlab

Mac:

* [Xcode][XC] for `clang` and `make`
* `gfortran` (possibly via [Homebrew][HB])
* Matlab

Windows:

* [MSYS2][MSYS2] or [MinGW-w64][MINGW]
* `make` (included in MSYS2)
* `gcc` (included in MinGW-w64)
* `gfortran` (included in MinGW-w64)
* BLAS library (e.g., OpenBLAS)
* Matlab (optional, for Matlab interface)

  [HB]: http://brew.sh/
  [XC]: http://itunes.apple.com/us/app/xcode/id497799835
  [MSYS2]: https://www.msys2.org/
  [MINGW]: https://www.mingw-w64.org/

Notes:

* The `matlab` binary must be on the system `PATH`.
* `python3` is required to generate the interface code.  However, the interface
  code is pre-generated and included in the repository.
* It is necessary to launch Xcode and accept the license agreement before
  building the interface.
* The smaller Xcode Command Line Tools package does not appear to work with
  Matlab 2015b.  The full Xcode install is required.

### Setup `mex`

Matlab's `mex` compiler driver must be configured to use the appropriate `C`
compiler.  This can be achieved by executing `mex -setup` from the Matlab prompt
or operating system terminal.  On Linux the selected compiler must be the
correct version of `gcc`.  On Mac OS X 10.9 the selected compiler must be
`clang`.  It is a good idea to match the compiler suggested on the Mathworks
[supported compilers][MC] page.  See this [note][MEX-XCODE-7] on Matlab
compatibility with Xcode 7.

  [MC]: http://www.mathworks.com/support/compilers/
  [MEX-XCODE-7]: http://www.mathworks.com/matlabcentral/answers/246507-why-can-t-mex-find-a-supported-compiler-in-matlab-r2015b-after-i-upgraded-to-xcode-7-0#answer_194526

### Install `gfortran` on Mac OS X

1. Install [Homebrew][HB]
2. `$ brew install gcc`

### Install Build Tools on Windows

1. Install [MSYS2][MSYS2] from https://www.msys2.org/
2. Open MSYS2 MinGW 64-bit terminal
3. Install required packages:
   ```bash
   pacman -S mingw-w64-x86_64-gcc
   pacman -S mingw-w64-x86_64-gcc-fortran
   pacman -S mingw-w64-x86_64-openblas
   pacman -S make
   ```
4. Add MinGW-w64 bin directory to system PATH (e.g., `C:\msys64\mingw64\bin`)

### Steps

From the base directory:

```
$ make
$ make matlab
```

Test:

```
$ make matlab_test
```

See <NOTES.md> for example build output.

### Notes

The basic requirements to build LUSOL are GNU `make`, `gfortran`, a C compiler,
and Matlab.  The build works with `gcc` on Linux and `clang` on Mac OS X.  It
may be necessary to modify the compiler variables in the `makefile` (`CC`,
`F90C`, and `F77C`) depending on the operating system and environment.

The `matlab` executable must be on the system path.  On Mac OS X with Matlab
R2015b this is achieved with:

```
$ export PATH=/Applications/MATLAB_R2015b.app/bin:$PATH
```

The `makefile` may have to be modified on Mac OS X depending on versions of
Matlab and `gfortran`.

## Authors

* **LUSOL Fortran code**: [Michael Saunders][MS]
* **Matlab interface**: [Nick Henderson][NWH]

  [MS]: http://www.stanford.edu/~saunders/
  [NWH]: http://www.stanford.edu/~nwh/
