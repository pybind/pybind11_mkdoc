import subprocess
import sys
from pathlib import Path

import pytest

DIR = Path(__file__).resolve().parent

with open(DIR / "sample_header_docs" / "sample_header_truth.h") as f:
    expected = f.read()


@pytest.mark.parametrize(
    "name",
    ["sample_header.h", "sample header with spaces.h"],
    ids=["no_spaces", "spaces"],
)
def test_simple_header_cli(tmp_path: Path, name: str) -> None:
    # Run pybind11-mkdoc and put the output in a temp file
    tf = tmp_path / "tmp.h"
    header = DIR / "sample_header_docs" / name
    subprocess.run([sys.executable, "-m", "pybind11_mkdoc", "-o", tf, header], check=True)

    # Ensure the header file matches
    res = tf.read_text(encoding="utf-8")

    assert res == expected
