import os
import sys

import pybind11_mkdoc

DIR = os.path.abspath(os.path.dirname(__file__))


def test_long_parameter(capsys):
    comments = pybind11_mkdoc.mkdoc_lib.extract_all([os.path.join(DIR, "long_parameter_docs", "long_parameter.h")])
    pybind11_mkdoc.mkdoc_lib.write_header(comments, sys.stdout)

    res = capsys.readouterr()
    expected = """\
Parameter ``x``:
    - Begin first parameter description. Senectus et netus et
    malesuada fames ac. End first parameter description.)doc";
"""

    assert expected in res.out
