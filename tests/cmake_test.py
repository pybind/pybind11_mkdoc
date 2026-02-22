import subprocess
from pathlib import Path

import pytest

DIR = Path(__file__).resolve().parent

with open(DIR / "cmake_docs" / "my_module_docs_truth.h") as f:
    expected = f.read()

def test_pybind11_mkdoc_cmake(tmp_path: Path) -> None:
    # Run pybind11-mkdoc and put the output in a temp file
    build_dir = tmp_path / "build"
    subprocess.run(["cmake", "-B", build_dir, "-S", DIR / "cmake_docs"], check=True)
    subprocess.run(["cmake", "--build", build_dir], check=True)

    # Ensure the header file matches
    res = (build_dir/"my_module_docs.h").read_text(encoding="utf-8")

    assert res == expected
