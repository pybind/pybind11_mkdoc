import re
from pathlib import Path

import pybind11_mkdoc

DIR = Path(__file__).resolve().parent

NAME_RE = re.compile(r"^static const char \*(\w+) =", re.MULTILINE)


def test_suffixed_names_do_not_collide(tmp_path):
    comments = pybind11_mkdoc.mkdoc_lib.extract_all([str(DIR / "duplicate_name_docs" / "duplicate_name.h")])

    output = tmp_path / "docs.h"
    with output.open("w") as fd:
        pybind11_mkdoc.mkdoc_lib.write_header(comments, fd)

    names = NAME_RE.findall(output.read_text())
    assert len(names) == len(comments)
    assert len(names) == len(set(names))
