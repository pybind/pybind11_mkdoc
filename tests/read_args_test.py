from pybind11_mkdoc.mkdoc_lib import read_args


def test_default_std():
    parameters, filenames = read_args(["sample.h"])
    assert "-std=c++17" in parameters
    assert filenames == ["sample.h"]


def test_explicit_std_wins():
    parameters, _ = read_args(["-std=c++11", "sample.h"])
    assert "-std=c++11" in parameters
    assert "-std=c++17" not in parameters
