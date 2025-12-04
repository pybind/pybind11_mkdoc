from pathlib import Path

import pybind11_mkdoc

DIR = Path(__file__).resolve().parent


def test_generate_headers(capsys, tmp_path):
    with open(DIR / "sample_header_docs" / "sample_header_truth.h") as f:
        expected = f.read()

    comments = pybind11_mkdoc.mkdoc_lib.extract_all([str(DIR / "sample_header_docs" / "sample_header.h")])
    assert [c[0] for c in comments] == ["mkd_doc_RootLevelSymbol", "mkd_doc_drake_MidLevelSymbol"]

    output = tmp_path / "docs.h"
    with output.open("w") as fd:
        pybind11_mkdoc.mkdoc_lib.write_header(comments, fd)

    res = capsys.readouterr()

    assert "warning" not in res.err
    assert "error" not in res.err
    assert output.read_text() == expected


def test_generate_headers_2(capsys, tmp_path):
    with open(DIR / "sample_header_docs" / "sample_header_2_truth.h") as f:
        expected = f.read()

    comments = pybind11_mkdoc.mkdoc_lib.extract_all([str(DIR / "sample_header_docs" / "sample_header_2.h")])

    output = tmp_path / "docs.h"
    with output.open("w") as fd:
        pybind11_mkdoc.mkdoc_lib.write_header(comments, fd)

    res = capsys.readouterr()

    assert "warning" not in res.err
    assert "error" not in res.err
    assert output.read_text() == expected
