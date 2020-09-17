# pybind11_mkdoc

[![CI](https://github.com/pybind/pybind11_mkdoc/workflows/CI/badge.svg)](https://github.com/pybind/pybind11_mkdoc/actions)

This tool processes a sequence of C/C++ headers and extracts comments that can
be referenced to generate docstrings in pybind11 binding code.


To install the latest development version:

```bash
python -m pip install git+git://github.com/pybind/pybind11_mkdoc.git@master
```

## Usage

To use this tool, simply invoke it with a list of header files. All output will
be written to ``stdout``, or to a filename provided via the ``-o`` parameter.

```bash
python -m pybind11_mkdoc -o docstrings.h header_file_1.h header_file_2.h
```

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

## Limitations

This tool supports Linux and macOS and requires Clang/LLVM to be installed. It
has never been used on Windows and will likely require adaptations.
