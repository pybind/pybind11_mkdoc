from pathlib import Path

import pybind11_mkdoc

DIR = Path(__file__).resolve().parent

with open(DIR / "sample_header_docs" / "sample_header_truth.h") as f:
    expected = f.read()


def test_generate_headers(capsys, tmp_path):
    comments = pybind11_mkdoc.mkdoc_lib.extract_all([str(DIR / "sample_header_docs" / "sample_header.h")])
    assert ["mkd_doc_RootLevelSymbol", "mkd_doc_drake_MidLevelSymbol"] == [c[0] for c in comments]

    output = tmp_path / "docs.h"
    with output.open("w") as fd:
        pybind11_mkdoc.mkdoc_lib.write_header(comments, fd)

    res = capsys.readouterr()

    assert "warning" not in res.err
    assert "error" not in res.err
    assert (output.read_text() == expected)
