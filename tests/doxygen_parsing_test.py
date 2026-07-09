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


def test_multiline_parameter_descriptions_with_mixed_indentation():
    comment = """/**
     * @brief Handles several inputs.
     *
     * @param alpha Alpha starts on the command line and continues
     *              with an indented line
     * and also continues without indentation.
     * @param[in] beta Beta starts with a direction.
     * More beta detail follows without indentation.
     * @arg gamma Gamma uses arg as a parameter alias.
     *             Gamma also has an indented continuation.
     * @tparam T Template text starts here.
     * More template text follows without indentation.
     */"""

    expected = """\
Handles several inputs.

Args:
    alpha: Alpha starts on the command line and continues with an
           indented line and also continues without indentation.
    beta [in]: Beta starts with a direction. More beta detail follows
               without indentation.
    gamma: Gamma uses arg as a parameter alias. Gamma also has an
           indented continuation.

Template Args:
    T: Template text starts here. More template text follows without
       indentation."""

    assert process_comment(comment) == expected


def test_multiline_return_raise_and_section_descriptions_with_mixed_indentation():
    comment = """/**
     * @brief Performs work.
     *
     * @return The result starts here
     *         and continues with indentation
     * and then continues without indentation.
     * @retval false Work was skipped
     * because the input was empty.
     * @throws RuntimeError Raised when work fails
     *                      after partial progress
     * and the failure detail is unindented.
     * @warning The warning starts here
     *          and continues with indentation
     * and also without indentation.
     * @note Notes can span
     * multiple lines without indentation too.
     * @par Custom Section
     * Custom section text can continue
     * without indentation.
     */"""

    expected = """\
Performs work.

Returns:
    The result starts here and continues with indentation and then
    continues without indentation.
    false: Work was skipped because the input was empty.

Raises:
    RuntimeError: Raised when work fails after partial progress and
                  the failure detail is unindented.

Warning:
    The warning starts here and continues with indentation and also
    without indentation.

Note:
    Notes can span multiple lines without indentation too.

Custom Section:
    Custom section text can continue without indentation."""

    assert process_comment(comment) == expected
