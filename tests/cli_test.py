import subprocess
import sys
from pathlib import Path

import pytest

from pybind11_mkdoc import _append_definition

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
    subprocess.run(
        [sys.executable, "-m", "pybind11_mkdoc", "-o", tf, header], check=True
    )

    # Ensure the header file matches
    res = tf.read_text(encoding="utf-8")

    assert res == expected


@pytest.mark.parametrize(
    ("definition", "expected_arg"),
    [
        ("FOO", "-DFOO=1"),
        ("FOO=", "-DFOO="),
        ("FOO=2", "-DFOO=2"),
        (" FOO = 2 ", "-DFOO=2"),
    ],
)
def test_append_definition(definition: str, expected_arg: str) -> None:
    args: list[str] = []
    _append_definition(args, definition)

    assert args == [expected_arg]


def test_parse_failure_sets_exit_code(tmp_path: Path) -> None:
    tf = tmp_path / "tmp.h"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pybind11_mkdoc",
            "-o",
            tf,
            tmp_path / "does_not_exist.h",
        ],
        check=False,
        capture_output=True,
    )

    assert result.returncode != 0
    assert not tf.exists()


def test_missing_include_reports_diagnostics(tmp_path: Path) -> None:
    header = tmp_path / "bad_header.h"
    header.write_text('#include "does_not_exist.h"\n', encoding="utf-8")
    tf = tmp_path / "tmp.h"
    result = subprocess.run(
        [sys.executable, "-m", "pybind11_mkdoc", "-o", tf, header],
        check=False,
        capture_output=True,
    )

    assert result.returncode != 0
    assert not tf.exists()
    assert "does_not_exist.h" in result.stderr.decode()
