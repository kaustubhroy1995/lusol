# Remove default rules
.SUFFIXES:

# detect operating system
OSLOWER := $(shell uname -s 2>/dev/null | tr [:upper:] [:lower:])
DARWIN := $(strip $(findstring darwin, $(OSLOWER)))
WINDOWS := $(strip $(findstring mingw, $(OSLOWER))$(findstring msys, $(OSLOWER))$(findstring cygwin, $(OSLOWER)))
ifeq ($(OS),Windows_NT)
  WINDOWS := windows
endif

# detect architecture on macOS (for Apple Silicon vs Intel)
ifneq ($(DARWIN),)
  ARCH := $(shell uname -m)
endif

# C compiler
ifneq ($(DARWIN),)
  # C compiler for macOS
  CC := clang
  CPPFLAGS :=
  ifeq ($(ARCH),arm64)
    # Apple Silicon (M1/M2/M3)
    CFLAGS := -arch arm64 -fPIC
  else
    # Intel Mac
    CFLAGS := -arch x86_64 -fPIC
  endif
else ifneq ($(WINDOWS),)
  # C compiler for windows
  CC := gcc
  CPPFLAGS :=
  CFLAGS := -m64
else
  # C compiler for linux
  CC := gcc
  CPPFLAGS :=
  CFLAGS := -m64 -fPIC
endif

# Fortran optimization level
FOPT := -O3

# Fortran compilers
ifneq ($(DARWIN),)
  # Fortran compilers for macOS
  F90C := gfortran
  F77C := gfortran
  ifeq ($(ARCH),arm64)
    # Apple Silicon (M1/M2/M3)
    F90FLAGS := -fPIC -Jsrc $(FOPT)
    F77FLAGS := -fPIC -fdefault-integer-8 $(FOPT)
  else
    # Intel Mac
    F90FLAGS := -m64 -fPIC -Jsrc $(FOPT)
    F77FLAGS := -m64 -fPIC -fdefault-integer-8 $(FOPT)
  endif
else ifneq ($(WINDOWS),)
  # Fortran compilers for windows
  F90C := gfortran
  F90FLAGS := -m64 -Jsrc $(FOPT)
  # Fortran 77 compiler
  F77C := gfortran
  F77FLAGS := -m64 -fdefault-integer-8 $(FOPT)
else
  # Fortran 90 compiler
  F90C := gfortran
  F90FLAGS :=  -m64 -fPIC -Jsrc $(FOPT)
  # Fortran 77 compiler
  F77C := gfortran
  F77FLAGS := -m64 -fPIC -fdefault-integer-8 $(FOPT)
endif

# Matlab
ML := matlab
MLFLAGS := -nojvm -nodisplay
ifneq ($(DARWIN),)
  # settings for macOS
  ifeq ($(ARCH),arm64)
    # Apple Silicon uses maca64
    MLARCH := maca64
  else
    # Intel Mac uses maci64
    MLARCH := maci64
  endif
else ifneq ($(WINDOWS),)
  # settings for windows
  MLARCH := win64
else
  # settings for linux
  MLARCH := glnxa64
endif

# Linker
ifneq ($(DARWIN),)
  # settings for macOS
  LD := clang
  LIB_SUFFIX := dylib
  EXPORT_SYMBOLS := src/symbols.osx
  LDFLAGS := -dynamiclib
  ifeq ($(ARCH),arm64)
    # Apple Silicon (M1/M2/M3)
    LDFLAGS += -arch arm64
  else
    # Intel Mac
    LDFLAGS += -arch x86_64
  endif
  LDFLAGS += -Wl,-twolevel_namespace
  LDFLAGS += -Wl,-no_compact_unwind
  LDFLAGS += -undefined error
  LDFLAGS += -bind_at_load
  LDFLAGS += -Wl,-exported_symbols_list,$(EXPORT_SYMBOLS)
  LDLIBS :=
  # Try to link against gfortran/quadmath/gcc libraries dynamically
  # Fall back to Homebrew paths if static libraries are not found
  LDLIBS += -lgfortran -lquadmath -lgcc_s.1
  # get blas from Matlab or system
  # For modern Matlab versions on Apple Silicon, use the appropriate architecture
  ifeq ($(ARCH),arm64)
    LDLIBS += -L/Applications/MATLAB_R2023b.app/bin/maca64 -lmwblas
  else
    LDLIBS += -L/Applications/MATLAB_R2015b.app/bin/maci64 -lmwblas
  endif
else ifneq ($(WINDOWS),)
  # settings for windows
  LD := gcc
  LIB_SUFFIX := dll
  EXPORT_SYMBOLS := src/symbols.def
  LDFLAGS := -m64 -shared
  LDFLAGS += -Wl,--out-implib,src/libclusol.dll.a
  LDFLAGS += $(EXPORT_SYMBOLS)
  # libraries
  LDLIBS :=
  LDLIBS += -lgfortran -lquadmath -lblas
else
  # settings for linux
  LD := gcc
  LIB_SUFFIX := so
  EXPORT_SYMBOLS := src/symbols.map
  LDFLAGS := -m64 -shared
  LDFLAGS += -Wl,--version-script,$(EXPORT_SYMBOLS)
  # libraries
  LDLIBS :=
  LDLIBS += -Wl,-rpath,/usr/lib -lgfortran -lblas
endif

# list of files required by matlab
MATLAB_FILES := \
  matlab/libclusol.$(LIB_SUFFIX) \
  matlab/clusol.h \
  matlab/libclusol_proto_$(MLARCH).m \
  matlab/libclusol_thunk_$(MLARCH).$(LIB_SUFFIX)

# list of interface specification files
INTERFACE_FILES := \
  gen/interface.py \
  gen/interface_files.org \
  gen/lu1fac.org \
  gen/lu6mul.org \
  gen/lu6sol.org \
  gen/lu8adc.org \
  gen/lu8adr.org \
  gen/lu8dlc.org \
  gen/lu8dlr.org \
  gen/lu8mod.org \
  gen/lu8rpc.org \
  gen/lu8rpr.org

# list of F77 code files
F77_FILES := \
  src/lusol_util.f \
  src/lusol6b.f \
  src/lusol7b.f \
  src/lusol8b.f

F77_OBJ := $(patsubst %.f,%.o,$(filter %.f,$(F77_FILES)))

# list of F90 code files
F90_FILES := \
  src/lusol_precision.f90 \
  src/lusol.f90

F90_OBJ := $(patsubst %.f90,%.o,$(filter %.f90,$(F90_FILES)))
F90_MOD := $(patsubst %.f90,%.mod,$(filter %.f90,$(F90_FILES)))

# list of object files
OBJ := src/clusol.o
OBJ += $(F90_OBJ)
OBJ += $(F77_OBJ)

# set the default goal
.DEFAULT_GOAL := all

# default target to build everything
.PHONY: all
all: src/libclusol.$(LIB_SUFFIX) src/clusol.h

# pattern to compile fortran 77 files
$(F77_OBJ) : %.o : %.f
	$(F77C) $(F77FLAGS) -c $< -o $@

# pattern to compile fortran 90 files
$(F90_OBJ) : %.o : %.f90
	$(F90C) $(F90FLAGS) -c $< -o $@

# dependencies for F90 module files
$(F90_MOD) : %.mod : %.o

# extra fortran dependencies
lusol.o : lusol_precision.mod

# C code generation
src/clusol.h: $(INTERFACE_FILES)
	./gen/interface.py -i gen/interface_files.org -o $@ -t header

src/clusol.c: $(INTERFACE_FILES)
	./gen/interface.py -i gen/interface_files.org -o $@ -t source

# C compilation
src/clusol.o: src/clusol.c src/clusol.h
	$(CC) $(CPPFLAGS) $(CFLAGS) -c $< -o $@

# Link the dynamic library
src/libclusol.$(LIB_SUFFIX): $(OBJ) $(EXPORT_SYMBOLS)
	$(LD) $(LDFLAGS) $(OBJ) -o $@ $(LDLIBS)

# file copying to matlab directory
$(MATLAB_FILES): src/libclusol.$(LIB_SUFFIX) src/clusol.h
	cp src/libclusol.$(LIB_SUFFIX) src/clusol.h ./matlab/
	$(ML) $(MLFLAGS) -r "cd matlab; lusol_build; exit"

.PHONY: matlab
matlab: $(MATLAB_FILES)

.PHONY: matlab_test
matlab_test: $(MATLAB_FILES)
	$(ML) $(MLFLAGS) -r "cd matlab; lusol_test; exit"

.PHONY: clean
clean:
	$(RM) src/*.o
	$(RM) src/*.$(LIB_SUFFIX)
	$(RM) src/*.dll.a
	$(RM) src/*.mod
	$(RM) $(MATLAB_FILES)

.PHONY: clean_gen
clean_gen:
	$(RM) src/clusol.h
	$(RM) src/clusol.c

# print helper
#print-%:
#	@echo $* := $($*)
