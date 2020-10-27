"""
This is a package for building pybind11 docstrings from C++ header comments.

(Docs WIP).
"""


import sys

from .mkdoc_lib import mkdoc


__version__ = "2.6.0"

def main(self):
    return mkdoc(sys.argv[:1])
