import os

import pytest
from clang import cindex

from pybind11_mkdoc import mkdoc_lib

CLT = "/Library/Developer/CommandLineTools/"
XCODE = "/Applications/Xcode.app/Contents/Developer/"


@pytest.fixture
def config_calls(monkeypatch):
    """Record cindex.Config.set_library_* calls instead of configuring libclang."""
    calls = {}
    monkeypatch.setattr(cindex.Config, "loaded", False)
    monkeypatch.setattr(cindex.Config, "set_library_file", lambda p: calls.__setitem__("file", p))
    monkeypatch.setattr(cindex.Config, "set_library_path", lambda p: calls.__setitem__("path", p))
    return calls


@pytest.fixture
def clean_env(monkeypatch):
    for var in ["LIBCLANG_PATH", "LLVM_DIR_PATH", "CLANG_INCLUDE_DIR", "CPP_INCLUDE_DIRS"]:
        monkeypatch.delenv(var, raising=False)


@pytest.fixture
def linux(monkeypatch):
    monkeypatch.setattr(mkdoc_lib.platform, "system", lambda: "Linux")


@pytest.fixture
def darwin(monkeypatch):
    monkeypatch.setattr(mkdoc_lib.platform, "system", lambda: "Darwin")


@pytest.fixture
def windows(monkeypatch):
    monkeypatch.setattr(mkdoc_lib.platform, "system", lambda: "Windows")


def fake_walk(subdirs):
    return lambda top: iter([(top, list(subdirs), [])])


@pytest.mark.usefixtures("linux", "clean_env")
def test_linux_libclang_path_without_llvm_dir(monkeypatch, config_calls, tmp_path):
    lib = tmp_path / "libclang.so.1"
    lib.touch()
    monkeypatch.setattr(mkdoc_lib, "glob", lambda _pattern: [])
    monkeypatch.setenv("LIBCLANG_PATH", str(lib))

    _, filenames = mkdoc_lib.read_args(["foo.h"])

    assert config_calls["file"] == str(lib)
    assert filenames == ["foo.h"]


@pytest.mark.usefixtures("linux", "clean_env")
def test_linux_libclang_path_without_llvm_dir_libcpp(monkeypatch, config_calls, tmp_path):
    lib = tmp_path / "libclang.so.1"
    lib.touch()
    monkeypatch.setattr(mkdoc_lib, "glob", lambda _pattern: [])
    monkeypatch.setenv("LIBCLANG_PATH", str(lib))

    parameters, _ = mkdoc_lib.read_args(["-stdlib=libc++", "foo.h"])

    assert config_calls["file"] == str(lib)
    assert "-stdlib=libc++" in parameters


@pytest.mark.usefixtures("linux", "clean_env", "config_calls")
def test_linux_no_llvm_dir_no_env_raises(monkeypatch):
    monkeypatch.setattr(mkdoc_lib, "glob", lambda _pattern: [])

    with pytest.raises(FileNotFoundError):
        mkdoc_lib.read_args(["foo.h"])


@pytest.mark.usefixtures("linux", "clean_env", "config_calls")
def test_linux_libclang_path_missing_raises(monkeypatch, tmp_path):
    monkeypatch.setattr(mkdoc_lib, "glob", lambda _pattern: [])
    monkeypatch.setenv("LIBCLANG_PATH", str(tmp_path / "does_not_exist.so.1"))

    with pytest.raises(FileNotFoundError):
        mkdoc_lib.read_args(["foo.h"])


@pytest.mark.usefixtures("darwin", "clean_env")
def test_macos_xcode_preferred(monkeypatch, config_calls):
    existing = {
        XCODE + "Toolchains/XcodeDefault.xctoolchain/usr/lib/libclang.dylib",
        XCODE + "Platforms/MacOSX.platform/Developer/SDKs",
        CLT + "usr/lib/libclang.dylib",
        CLT + "SDKs",
    }
    monkeypatch.setattr(os.path, "exists", lambda p: p in existing)
    monkeypatch.setattr(os, "walk", fake_walk(["MacOSX.sdk"]))

    parameters, _ = mkdoc_lib.read_args(["foo.h"])

    assert config_calls["path"] == XCODE + "Toolchains/XcodeDefault.xctoolchain/usr/lib"
    idx = parameters.index("-isysroot")
    assert parameters[idx + 1] == XCODE + "Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk"


@pytest.mark.usefixtures("darwin", "clean_env")
def test_macos_command_line_tools_fallback(monkeypatch, config_calls):
    existing = {CLT + "usr/lib/libclang.dylib", CLT + "SDKs"}
    monkeypatch.setattr(os.path, "exists", lambda p: p in existing)
    monkeypatch.setattr(os, "walk", fake_walk(["MacOSX.sdk", "MacOSX26.0.sdk"]))

    parameters, _ = mkdoc_lib.read_args(["foo.h"])

    assert config_calls["path"] == CLT + "usr/lib"
    idx = parameters.index("-isysroot")
    assert parameters[idx + 1] == CLT + "SDKs/MacOSX.sdk"


@pytest.mark.usefixtures("darwin", "clean_env")
def test_macos_libclang_path_env(monkeypatch, config_calls, tmp_path):
    lib = tmp_path / "libclang.dylib"
    lib.touch()
    monkeypatch.setenv("LIBCLANG_PATH", str(lib))
    monkeypatch.setattr(os.path, "exists", lambda _p: False)

    parameters, _ = mkdoc_lib.read_args(["foo.h"])

    assert config_calls["file"] == str(lib)
    assert "-isysroot" not in parameters


@pytest.mark.usefixtures("darwin", "clean_env", "config_calls")
def test_macos_libclang_path_env_missing_raises(monkeypatch, tmp_path):
    monkeypatch.setenv("LIBCLANG_PATH", str(tmp_path / "does_not_exist.dylib"))

    with pytest.raises(FileNotFoundError):
        mkdoc_lib.read_args(["foo.h"])


@pytest.mark.usefixtures("windows", "clean_env")
def test_windows_libclang_path_env(monkeypatch, config_calls, tmp_path):
    lib = tmp_path / "libclang.dll"
    lib.touch()
    monkeypatch.setenv("LIBCLANG_PATH", str(lib))

    _, filenames = mkdoc_lib.read_args(["foo.h"])

    assert config_calls["file"] == str(lib)
    assert filenames == ["foo.h"]


@pytest.mark.usefixtures("windows", "clean_env", "config_calls")
def test_windows_libclang_path_env_missing_raises(monkeypatch, tmp_path):
    monkeypatch.setenv("LIBCLANG_PATH", str(tmp_path / "does_not_exist.dll"))

    with pytest.raises(FileNotFoundError):
        mkdoc_lib.read_args(["foo.h"])


@pytest.mark.usefixtures("darwin", "clean_env", "config_calls")
def test_macos_sdk_newest_numeric(monkeypatch):
    existing = {CLT + "usr/lib/libclang.dylib", CLT + "SDKs"}
    monkeypatch.setattr(os.path, "exists", lambda p: p in existing)
    # No MacOSX.sdk; lexical sort would wrongly pick MacOSX9.sdk as newest
    monkeypatch.setattr(os, "walk", fake_walk(["MacOSX9.sdk", "MacOSX10.1.sdk"]))

    parameters, _ = mkdoc_lib.read_args(["foo.h"])

    idx = parameters.index("-isysroot")
    assert parameters[idx + 1] == CLT + "SDKs/MacOSX10.1.sdk"


def test_default_std():
    parameters, filenames = mkdoc_lib.read_args(["sample.h"])
    assert "-std=c++17" in parameters
    assert filenames == ["sample.h"]


def test_explicit_std_wins():
    parameters, _ = mkdoc_lib.read_args(["-std=c++11", "sample.h"])
    assert "-std=c++11" in parameters
    assert "-std=c++17" not in parameters
