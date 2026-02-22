import os
import subprocess
from pathlib import Path

import pytest

DIR = Path(__file__).resolve().parent


def test_pybind11_mkdoc_cmake(tmp_path: Path) -> None:
    # Run pybind11-mkdoc and put the output in a temp file
    build_dir = tmp_path / "build"
    subprocess.run(["cmake", "-B", build_dir, "-S", DIR / "cmake_docs"], check=True)
    subprocess.run(["cmake", "--build", build_dir], check=True)

    # Ensure the header file matches
    res = (build_dir/"my_module_docs.h").read_text(encoding="utf-8")

    with open(DIR / "cmake_docs" / "my_module_docs_truth.h") as f:
        expected = f.read()

    assert res == expected

def test_pybind11_mkdoc_cmake_extra_args(tmp_path: Path) -> None:
    # Run pybind11-mkdoc and put the output in a temp file
    build_dir = tmp_path / "build"
    env = os.environ.copy()
    env["PYBIND11_TEST_EXTRA_ARGS"] = "-DMY_EXTRA_DEFINE=1"

    subprocess.run(["cmake", "-B", build_dir, "-S", DIR / "cmake_docs"], check=True, env=env)
    subprocess.run(["cmake", "--build", build_dir], check=True, env=env)

    # Ensure the header file matches
    res = (build_dir/"my_module_docs.h").read_text(encoding="utf-8")

    with open(DIR / "cmake_docs" / "my_module_docs_extra_truth.h") as f:
        expected = f.read()

    assert res == expected
