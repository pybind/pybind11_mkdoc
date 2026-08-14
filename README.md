# pybind11_mkdoc

[![CI](https://github.com/pybind/pybind11_mkdoc/workflows/CI/badge.svg)](https://github.com/pybind/pybind11_mkdoc/actions)

This tool processes a sequence of C/C++ headers and extracts comments that can
be referenced to generate docstrings in pybind11 binding code.


To install the latest development version:

```bash
python -m pip install git+https://github.com/pybind/pybind11_mkdoc.git
```

## Usage

To use this tool, simply invoke it with a list of header files. All output will
be written to ``stdout``, or to a filename provided via the ``-o`` parameter.

```bash
python -m pybind11_mkdoc -o docstrings.h header_file_1.h header_file_2.h
```

Optionally, the path to the `libclang.so` and LLVM directory can be specified by setting the LIBCLANG_PATH and LLVM_DIR_PATH environment variables respectively.

Suppose we provide an input file with the following contents:

```cpp
/// Docstring 1
class MyClass {

    /// Docstring 2
    MyClass() {
    }

    /// Docstring 3
    void foo() {
    }

    /// Docstring 4 for overload
    void foo(int bar) {
    }

    /// Docstring 5 for yet another overload
    void foo(int bar, int baz) {
    }
};
```

Once processed via ``pybind11_mkdoc``, the docstrings can be accessed as follows
from pybind11 binding code:

```cpp
#include "docstrings.h"

const char *docstring_1 = DOC(MyClass);
const char *docstring_2 = DOC(MyClass, MyClass);
const char *docstring_3 = DOC(MyClass, foo);
const char *docstring_4 = DOC(MyClass, foo, 2);
const char *docstring_5 = DOC(MyClass, foo, 3);
```

Note the counter suffix for repeated definitions and docstrings. Namespaces and
nested classes are also supported, in which case the number of arguments to the
``DOC`` macro simply increases.

In practice, the docstrings are likely referenced in a matching set of binding
declarations:

```cpp

py::class_<MyClass>(m, "MyClass", DOC(MyClass))
    .def(py::init<>(), DOC(MyClass, MyClass))
    ...
```

### CMake
The `pybind11_mkdoc` CMake function is included to easily generate header for a pybind11 module when
compiling said module in CMake. The function generates the headers based on the arguments provided.
In addition, it add target dependencies so the pybind11-mkdoc header file is generated before
the pybind11 module. Also, it will automatically add the current binary directory to the pybind11
module's includes, so it can easily be included when compiling the module.

The required parameters are:
* OUTPUT - The name of the output file.
* PYBIND11_MODULE - The pybind11 module target that these docs will be used for.
* HEADERS - The header files to create docs for. These can be absolute paths or relative to the
            current source directory.

The optional parameters are:
* EXTRA_ARGS - This string argument will be added verbatim to the pybind11-mkdoc command.

Below is an example of how it is used:
```cmake
# Find pybind11-mkdoc
# This assumes you have already run a find_package for Python.
execute_process(
    COMMAND ${Python_EXECUTABLE} -c "import pybind11_mkdoc; print(pybind11_mkdoc.get_cmake_dir())"
    OUTPUT_VARIABLE pybind11_mkdoc_DIR
    OUTPUT_STRIP_TRAILING_WHITESPACE
)
find_package(pybind11_mkdoc REQUIRED CONFIG)

# Add the pybind11 module
pybind11_add_module(my_pybind11_module my_src_files.cc)
pybind11_mkdoc(
    OUTPUT my_pybind11_module_docs.h
    PYBIND11_MODULE my_pybind11_module
    HEADERS
        header_1.h
        /absolute/path/to/header_2.h
)
```
## Limitations

This tool supports Linux and macOS for Python versions 3.9 to 3.14.  Also, it
requires Clang/LLVM to be installed.


## Testing

Install the packages `pytest`, `pytest-forked` and `pybind11`:
```
python3 -m pip install pytest pytest-forked pybind11
```

Next, install this project:
```
python3 -m pip install .
```

And execute the tests (forked)
```
python3 -m pytest --forked
```
