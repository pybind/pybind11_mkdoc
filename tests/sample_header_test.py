import os

import pybind11_mkdoc

DIR = os.path.abspath(os.path.dirname(__file__))


def test_generate_headers(capsys, tmp_path):
    comments = pybind11_mkdoc.mkdoc_lib.extract_all([os.path.join(DIR, "sample_header_docs", "sample_header.h")])
    assert ["mkd_doc_RootLevelSymbol", "mkd_doc_drake_MidLevelSymbol"] == [c[0] for c in comments]

    output = tmp_path / "docs.h"
    with output.open("w") as fd:
        pybind11_mkdoc.mkdoc_lib.write_header(comments, fd)

    res = capsys.readouterr()

    assert "warning" not in res.err
    assert "error" not in res.err
    assert (
        output.read_text()
        == """\
/*
  This file contains docstrings for use in the Python bindings.
  Do not edit! They were automatically extracted by pybind11_mkdoc.
 */

#define MKD_EXPAND(x)                                      x
#define MKD_COUNT(_1, _2, _3, _4, _5, _6, _7, COUNT, ...)  COUNT
#define MKD_VA_SIZE(...)                                   MKD_EXPAND(MKD_COUNT(__VA_ARGS__, 7, 6, 5, 4, 3, 2, 1, 0))
#define MKD_CAT1(a, b)                                     a ## b
#define MKD_CAT2(a, b)                                     MKD_CAT1(a, b)
#define MKD_DOC1(n1)                                       mkd_doc_##n1
#define MKD_DOC2(n1, n2)                                   mkd_doc_##n1##_##n2
#define MKD_DOC3(n1, n2, n3)                               mkd_doc_##n1##_##n2##_##n3
#define MKD_DOC4(n1, n2, n3, n4)                           mkd_doc_##n1##_##n2##_##n3##_##n4
#define MKD_DOC5(n1, n2, n3, n4, n5)                       mkd_doc_##n1##_##n2##_##n3##_##n4##_##n5
#define MKD_DOC7(n1, n2, n3, n4, n5, n6, n7)               mkd_doc_##n1##_##n2##_##n3##_##n4##_##n5##_##n6##_##n7
#define DOC(...)                                           MKD_EXPAND(MKD_EXPAND(MKD_CAT2(MKD_DOC, MKD_VA_SIZE(__VA_ARGS__)))(__VA_ARGS__))

#if defined(__GNUG__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wunused-variable"
#endif


static const char *mkd_doc_RootLevelSymbol =
R"doc(Root-level symbol. Magna fermentum iaculis eu non diam phasellus
vestibulum.)doc";

static const char *mkd_doc_drake_MidLevelSymbol =
R"doc(1. Begin first ordered list element. Rutrum quisque non tellus orci ac
auctor. End first ordered list element. 2. Begin second ordered list
element. Ipsum faucibus vitae aliquet nec. Ligula ullamcorper
malesuada proin libero. End second ordered list element. 3. Begin
third ordered list element. Dictum sit amet justo donec enim. Pharetra
convallis posuere morbi leo urna molestie. End third ordered list
element.

Senectus et netus et malesuada fames ac. Tincidunt lobortis feugiat
vivamus at augue eget arcu dictum varius.)doc";

#if defined(__GNUG__)
#pragma GCC diagnostic pop
#endif

"""
    )
