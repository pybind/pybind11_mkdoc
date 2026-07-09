from pybind11_mkdoc.mkdoc_lib import process_comment


def test_doxygen_sections_and_continuations():
    comment = """/**
     * @brief Parses a value.
     * Continues the brief text.
     *
     * @param[in] input Input text.
     *                  Continuation keeps belonging to input.
     * @param[out] output Output text.
     * @tparam T Template value type.
     * @retval true When parsing succeeds.
     * @throws std::runtime_error When parsing fails.
     * @exception std::logic_error When parsing is inconsistent.
     *
     * @warning Check the input first.
     *          Continuation remains in the warning.
     * @note This note is preserved.
     * @pre Parser is initialized.
     * @post Output contains parsed data.
     * @see OtherParser
     * @deprecated Use parse2 instead.
     */"""

    expected = """\
Parses a value. Continues the brief text.

Args:
    input [in]: Input text. Continuation keeps belonging to input.
    output [out]: Output text.

Template Args:
    T: Template value type.

Returns:
    true: When parsing succeeds.

Raises:
    std::runtime_error: When parsing fails.
    std::logic_error: When parsing is inconsistent.

Warning:
    Check the input first. Continuation remains in the warning.

Note:
    This note is preserved.

Precondition:
    Parser is initialized.

Postcondition:
    Output contains parsed data.

See also:
    OtherParser

Deprecated:
    Use parse2 instead."""

    assert process_comment(comment) == expected


def test_doxygen_code_and_whitespace():
    comment = """/**
     * Ordered list:
     *
     * 1. First item has a continuation that should align under the text
     *    instead of starting a new paragraph.
     * 2. Second item.
     *
     * @code
     * int value = 1;
     * value += 2;
     * @endcode
     */"""

    expected = """\
Ordered list:

1. First item has a continuation that should align under the text
   instead of starting a new paragraph.
2. Second item.

```
int value = 1;
value += 2;
```"""

    assert process_comment(comment) == expected
