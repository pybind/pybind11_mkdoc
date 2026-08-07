#!/usr/bin/env python3
#
#  Syntax: mkdoc.py [-I<path> ..] [.. a list of header files ..]
#
#  Extract documentation from C++ header files to use it in Python bindings
#

from __future__ import annotations

import contextlib
import ctypes.util
import os
import platform
import re
import sys
import textwrap
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from glob import glob
from itertools import repeat

from clang import cindex
from clang.cindex import CursorKind

RECURSE_LIST = [
    CursorKind.TRANSLATION_UNIT,
    CursorKind.NAMESPACE,
    CursorKind.CLASS_DECL,
    CursorKind.STRUCT_DECL,
    CursorKind.ENUM_DECL,
    CursorKind.CLASS_TEMPLATE,
]

PRINT_LIST = [
    CursorKind.CLASS_DECL,
    CursorKind.STRUCT_DECL,
    CursorKind.ENUM_DECL,
    CursorKind.ENUM_CONSTANT_DECL,
    CursorKind.CLASS_TEMPLATE,
    CursorKind.FUNCTION_DECL,
    CursorKind.FUNCTION_TEMPLATE,
    CursorKind.CONVERSION_FUNCTION,
    CursorKind.CXX_METHOD,
    CursorKind.CONSTRUCTOR,
    CursorKind.FIELD_DECL,
]

FUNCTION_DOCSTRING_LIST = [
    CursorKind.FUNCTION_DECL,
    CursorKind.FUNCTION_TEMPLATE,
    CursorKind.CONVERSION_FUNCTION,
    CursorKind.CXX_METHOD,
    CursorKind.CONSTRUCTOR,
]

PREFIX_BLACKLIST = [CursorKind.TRANSLATION_UNIT]

CPP_OPERATORS = {
    "<=": "le",
    ">=": "ge",
    "==": "eq",
    "!=": "ne",
    "[]": "array",
    "+=": "iadd",
    "-=": "isub",
    "*=": "imul",
    "/=": "idiv",
    "%=": "imod",
    "&=": "iand",
    "|=": "ior",
    "^=": "ixor",
    "<<=": "ilshift",
    ">>=": "irshift",
    "++": "inc",
    "--": "dec",
    "<<": "lshift",
    ">>": "rshift",
    "&&": "land",
    "||": "lor",
    "!": "lnot",
    "~": "bnot",
    "&": "band",
    "|": "bor",
    "+": "add",
    "-": "sub",
    "*": "mul",
    "/": "div",
    "%": "mod",
    "<": "lt",
    ">": "gt",
    "=": "assign",
    "()": "call",
}

CPP_OPERATORS = OrderedDict(sorted(CPP_OPERATORS.items(), key=lambda t: -len(t[0])))

docstring_width = 70


class NoFilenamesError(ValueError):
    pass


def d(s):
    return s if isinstance(s, str) else s.decode("utf8")


def sanitize_name(name):
    name = re.sub(r"type-parameter-0-([0-9]+)", r"T\1", name)
    for k, v in CPP_OPERATORS.items():
        name = name.replace(f"operator{k}", f"operator_{v}")
    name = re.sub("<.*>", "", name)
    name = "".join([ch if ch.isalnum() else "_" for ch in name])
    name = re.sub("_$", "", re.sub("_+", "_", name))
    return "mkd_doc_" + name


section_command_re = re.compile(r"\s*[\\@](\w+)(?:\[([^\]]+)\])?(?:\s+(.*))?$")
code_segment_re = re.compile(r"(```)")
prefix_re = re.compile(r"(\s*)((?:[*\-•]\s)|(?:\(?\d+[\.)]\s)|(?:[\w:]+(?:\s+\[[^\]]+\])?:(?:\s+|$)))")
param_arg_re = re.compile(r"([\w:]+)\s*(.*)")
raises_arg_re = re.compile(r"([\w:]+)\s*(.*)")

IGNORED_DOXYGEN_COMMANDS = {
    "addtogroup",
    "class",
    "def",
    "defgroup",
    "dir",
    "enum",
    "file",
    "fn",
    "ingroup",
    "interface",
    "mainpage",
    "name",
    "namespace",
    "overload",
    "package",
    "page",
    "private",
    "protected",
    "public",
    "relates",
    "relatesalso",
    "struct",
    "typedef",
    "union",
    "var",
    "weakgroup",
}

SECTION_HEADINGS = {
    "attention": "Attention",
    "author": "Author",
    "authors": "Authors",
    "bug": "Bug",
    "copyright": "Copyright",
    "date": "Date",
    "deprecated": "Deprecated",
    "invariant": "Invariant",
    "note": "Note",
    "par": None,
    "post": "Postcondition",
    "pre": "Precondition",
    "remark": "Remark",
    "remarks": "Remarks",
    "result": "Returns",
    "retval": "Returns",
    "return": "Returns",
    "returns": "Returns",
    "sa": "See also",
    "see": "See also",
    "since": "Since",
    "todo": "Todo",
    "version": "Version",
    "warning": "Warning",
}

INLINE_DOXYGEN_REPLACEMENTS = [
    (re.compile(r"[\\@][cp]\s+([^\s]+)"), r"``\1``"),
    (re.compile(r"[\\@](?:a|e|em)\s+([^\s]+)"), r"*\1*"),
    (re.compile(r"[\\@]b\s+([^\s]+)"), r"**\1**"),
    (re.compile(r"[\\@]ref\s+([^\s]+)"), r"\1"),
]


def _format_named_entries(heading, entries):
    if not entries:
        return []
    lines = [f"{heading}:"]
    lines += [f"    {name}: {text}" for name, text in entries]
    lines.append("")
    return lines


def _format_list_entries(heading, entries):
    if not entries:
        return []
    lines = [f"{heading}:"]
    lines += [f"    {text}" for text in entries]
    lines.append("")
    return lines


def _format_section_entries(entries):
    lines = []
    for heading, text in entries:
        lines.append(f"{heading}:")
        if text:
            lines.append(f"    {text}")
        lines.append("")
    return lines


def _append_continuation(target, text):
    text = text.strip()
    if not text:
        return
    if target[0] == "body":
        target[1].append(text)
    elif target[0] == "brief":
        if target[1] and target[1][-1].rstrip().endswith((".", "!", "?")):
            target[1].append("")
        target[1].append(text)
    elif target[0] == "section":
        target[1][-1][1].append(text)
    elif target[0] == "list":
        entries = target[1]
        index = target[2]
        entries[index] = f"{entries[index]} {text}".strip()
    else:
        entries = target[1]
        index = target[2]
        name, value = entries[index]
        entries[index] = (name, f"{value} {text}".strip())


def _consume_doxygen_sections(s):
    lines = s.splitlines()
    body_lines = []
    params = []
    t_params = []
    returns = []
    raises = []
    sections = []
    active = None
    pending_brief_separator = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            body_lines.append(line)
            active = None
            pending_brief_separator = False
            continue

        m = section_command_re.match(line)
        if not m:
            if active is not None:
                _append_continuation(active, line)
            else:
                if pending_brief_separator:
                    body_lines.append("")
                    pending_brief_separator = False
                body_lines.append(line)
            continue

        command, option, rest = m.groups()
        command = command.lower()
        rest = (rest or "").strip()

        if pending_brief_separator and command in {"details", "short"}:
            body_lines.append("")
            pending_brief_separator = False

        if command in {"brief", "short"}:
            if rest:
                body_lines.append(rest)
                pending_brief_separator = True
                active = ("brief", body_lines)
            else:
                active = None
            continue

        if command == "details":
            if rest:
                body_lines.append(rest)
                active = ("body", body_lines)
            else:
                active = None
            continue

        if command in {"param", "arg"}:
            arg = param_arg_re.match(rest)
            if arg:
                name, text = arg.groups()
                if option:
                    name = f"{name} [{option}]"
                params.append((name, text.strip()))
                active = ("entry", params, len(params) - 1)
            else:
                active = None
            continue

        if command in {"tparam", "typeparam"}:
            arg = param_arg_re.match(rest)
            if arg:
                name, text = arg.groups()
                t_params.append((name, text.strip()))
                active = ("entry", t_params, len(t_params) - 1)
            else:
                active = None
            continue

        if command in {"return", "returns", "result"}:
            if rest:
                returns.append(rest)
                active = ("list", returns, len(returns) - 1)
            else:
                active = None
            continue

        if command == "retval":
            arg = param_arg_re.match(rest)
            if arg:
                name, text = arg.groups()
                returns.append(f"{name}: {text.strip()}" if text else name)
                active = ("list", returns, len(returns) - 1)
            else:
                active = None
            continue

        if command in {"exception", "throw", "throws"}:
            arg = raises_arg_re.match(rest)
            if arg:
                name, text = arg.groups()
                raises.append((name, text.strip()))
                active = ("entry", raises, len(raises) - 1)
            else:
                active = None
            continue

        if command in IGNORED_DOXYGEN_COMMANDS:
            active = None
            continue

        if command in SECTION_HEADINGS:
            heading = SECTION_HEADINGS[command]
            if heading is None:
                heading = rest.strip().rstrip(":") or "Note"
                rest = ""
            sections.append([heading, [rest] if rest else []])
            active = ("section", sections)
            continue

        if active is not None:
            _append_continuation(active, line)
        else:
            body_lines.append(line)

    result = list(body_lines)
    while result and not result[-1].strip():
        result.pop()
    if result and (params or t_params or returns or raises or sections):
        result.append("")
    result += _format_named_entries("Args", params)
    result += _format_named_entries("Template Args", t_params)
    result += _format_list_entries("Returns", returns)
    result += _format_named_entries("Raises", raises)
    result += _format_section_entries((heading, " ".join(text).strip()) for heading, text in sections)
    return "\n".join(result)


def process_comment(comment):
    # For declarations that have no raw comment; skip the full normalization pipeline.
    if not comment:
        return ""

    result_lines = []

    # Remove C++ comment syntax
    leading_spaces = float("inf")
    for s in comment.expandtabs(tabsize=4).splitlines():
        s = s.strip()
        if s.endswith("*/"):
            s = s[:-2].rstrip("*")
        if s.startswith("/*"):
            s = s[2:].lstrip("*!<")
        elif s.startswith("//"):
            s = s[2:].lstrip("/!<")
        elif s.startswith("*"):
            s = s[1:]
        if len(s) > 0:
            leading_spaces = min(leading_spaces, len(s) - len(s.lstrip()))
        result_lines.append(s)

    if leading_spaces != float("inf"):
        result = "\n".join(s[leading_spaces:] for s in result_lines) + "\n"
    else:
        result = "\n".join(result_lines) + "\n"

    s = result
    for pattern, replacement in INLINE_DOXYGEN_REPLACEMENTS:
        s = pattern.sub(replacement, s)

    s = re.sub(r"[\\@]code\s?(.*?)\s?[\\@]endcode", r"```\n\1\n```\n", s, flags=re.DOTALL)
    s = re.sub(r"[\\@]verbatim\s?(.*?)\s?[\\@]endverbatim", r"```\n\1\n```\n", s, flags=re.DOTALL)
    s = _consume_doxygen_sections(s)

    # HTML/TeX tags
    s = re.sub(r"<tt>(.*?)</tt>", r"``\1``", s, flags=re.DOTALL)
    s = re.sub(r"<pre>(.*?)</pre>", r"```\n\1\n```\n", s, flags=re.DOTALL)
    s = re.sub(r"<em>(.*?)</em>", r"*\1*", s, flags=re.DOTALL)
    s = re.sub(r"<b>(.*?)</b>", r"**\1**", s, flags=re.DOTALL)
    s = re.sub(r"[\\@]f\$(.*?)[\\@]f\$", r":math:`\1`", s, flags=re.DOTALL)
    s = re.sub(r"<li>", r"\n\n* ", s)
    s = re.sub(r"</?ul>", r"", s)
    s = re.sub(r"</li>", r"\n\n", s)

    s = s.replace("``true``", "``True``")
    s = s.replace("``false``", "``False``")

    # Re-flow text
    wrapper = textwrap.TextWrapper()
    wrapper.expand_tabs = True
    wrapper.replace_whitespace = True
    wrapper.drop_whitespace = True
    wrapper.width = docstring_width
    wrapper.initial_indent = wrapper.subsequent_indent = ""

    result = []
    in_code_segment = False
    for x in code_segment_re.split(s):
        if x == "```":
            if not in_code_segment:
                if result and result[-1] and not result[-1].endswith("\n\n"):
                    result[-1] += "\n"
                result.append("```\n")
            else:
                result.append("\n```\n\n")
            in_code_segment = not in_code_segment
        elif in_code_segment:
            result.append(x.strip())
        else:
            wrapped = []
            paragraph = []

            def get_prefix_and_indent(line) -> tuple[str | None, str]:
                indent = len(line) - len(line.lstrip())
                indent_str = " " * indent
                m = prefix_re.match(line)
                if m:
                    prefix = m.group(0)
                    return prefix, " " * len(prefix)
                return None, indent_str

            def flush_paragraph(paragraph=paragraph, wrapped=wrapped):
                if not paragraph:
                    return

                # Detect bullet/number from first line
                first_line = paragraph[0]
                prefix, indent_str = get_prefix_and_indent(first_line)

                # Combine paragraph into single string (replace internal line breaks with space)
                para_text = " ".join(line.strip() for line in paragraph)

                if prefix:
                    content = para_text[len(prefix.lstrip()) :]
                    wrapper.initial_indent = prefix
                    wrapper.subsequent_indent = indent_str
                    if content == "":
                        # This paragraph is just the prefix
                        wrapped.append(prefix)
                        paragraph.clear()
                        return
                else:
                    content = para_text.lstrip()
                    wrapper.initial_indent = indent_str
                    wrapper.subsequent_indent = indent_str

                wrapped.append(wrapper.fill(content))
                paragraph.clear()

            current_prefix = None
            current_indent = ""
            for line in x.splitlines():
                if not line.strip():
                    flush_paragraph()
                    wrapped.append(line)  # preserve blank lines
                    continue

                prefix, indent = get_prefix_and_indent(line)
                if paragraph and ((indent != current_indent) or (prefix and prefix != current_prefix)):
                    # Prefix/indent changed → start new paragraph
                    flush_paragraph()

                paragraph.append(line)
                current_prefix = prefix
                current_indent = indent

            flush_paragraph()
            result.append("\n".join(wrapped))
    return "".join(result).rstrip().lstrip("\n")


def format_function_docstring(comment):
    if not comment:
        return ""
    comment = comment.rstrip()
    if "\n" not in comment:
        return comment
    return comment + "\n\n"


def _is_cursor_from_file(node, filename, file_cache):
    if node.location.file is None:
        return True

    node_filename = d(node.location.file.name)
    # libclang often reports many cursors from the same file; avoid repeated stat calls by caching.
    if node_filename not in file_cache:
        file_cache[node_filename] = os.path.samefile(node_filename, filename)
    return file_cache[node_filename]


def extract(filename, node, prefix, output, file_cache):
    if not _is_cursor_from_file(node, filename, file_cache):
        return 0
    if node.kind in RECURSE_LIST:
        sub_prefix = prefix
        if node.kind not in PREFIX_BLACKLIST:
            if len(sub_prefix) > 0:
                sub_prefix += "_"
            sub_prefix += d(node.spelling)
        for i in node.get_children():
            extract(filename, i, sub_prefix, output, file_cache)
    if node.kind in PRINT_LIST:
        comment = d(node.raw_comment) if node.raw_comment is not None else ""
        comment = process_comment(comment)
        if node.kind in FUNCTION_DOCSTRING_LIST:
            comment = format_function_docstring(comment)
        sub_prefix = prefix
        if len(sub_prefix) > 0:
            sub_prefix += "_"
        if len(node.spelling) > 0:
            name = sanitize_name(sub_prefix + d(node.spelling))
            output.append((name, filename, comment))
            return None
        return None
    return None


def _report_diagnostics(filename, tu):
    """Print clang diagnostics to stderr and fail if any of them is an error."""
    errors = 0
    for diagnostic in tu.diagnostics:
        sys.stderr.write(diagnostic.format() + "\n")
        if diagnostic.severity >= cindex.Diagnostic.Error:
            errors += 1
    if errors:
        msg = f"Clang reported {errors} error(s) while parsing {filename}"
        raise RuntimeError(msg)


def _extract_file(filename, parameters):
    # Diagnostics are printed by _report_diagnostics, not by libclang itself.
    index = cindex.Index(cindex.conf.lib.clang_createIndex(False, False))
    tu = index.parse(filename, parameters)
    _report_diagnostics(filename, tu)
    output = []
    extract(filename, tu.cursor, "", output, {})
    return output


def read_args(args):
    parameters = []
    filenames = []
    if "-x" not in args:
        parameters.extend(["-x", "c++"])
    if not any(it.startswith("-std=") for it in args):
        parameters.append("-std=c++11")
    parameters.append("-Wno-pragma-once-outside-header")

    if platform.system() == "Darwin":
        dev_path = "/Applications/Xcode.app/Contents/Developer/"
        lib_dir = dev_path + "Toolchains/XcodeDefault.xctoolchain/usr/lib/"
        sdk_dir = dev_path + "Platforms/MacOSX.platform/Developer/SDKs"
        libclang = lib_dir + "libclang.dylib"

        # cindex forbids (re)configuring the library once it has been loaded
        if os.path.exists(libclang) and not cindex.Config.loaded:
            cindex.Config.set_library_path(os.path.dirname(libclang))

        if os.path.exists(sdk_dir):
            sysroot_dir = os.path.join(sdk_dir, next(os.walk(sdk_dir))[1][0])
            parameters.append("-isysroot")
            parameters.append(sysroot_dir)
    elif platform.system() == "Windows":
        if "LIBCLANG_PATH" in os.environ:
            library_file = os.environ["LIBCLANG_PATH"]
            if os.path.isfile(library_file):
                if not cindex.Config.loaded:
                    cindex.Config.set_library_file(library_file)
            else:
                msg = "Failed to find libclang.dll! Set the LIBCLANG_PATH environment variable to provide a path to it."
                raise FileNotFoundError(msg)
        else:
            library_file = ctypes.util.find_library("libclang.dll")
            if library_file is not None and not cindex.Config.loaded:
                cindex.Config.set_library_file(library_file)
    elif platform.system() == "Linux":
        # LLVM switched to a monolithical setup that includes everything under
        # /usr/lib/llvm{version_number}/. We glob for the library and select
        # the highest version
        def folder_version(d):
            return [int(ver) for ver in re.findall(r"(?<!lib)(?<!\d)\d+", d)]

        llvm_dir = max(
            (
                path
                for libdir in ["lib64", "lib", "lib32"]
                for path in glob(f"/usr/{libdir}/llvm-*")
                if os.path.exists(os.path.join(path, "lib", "libclang.so.1"))
            ),
            default=None,
            key=folder_version,
        )

        # Ability to override LLVM/libclang paths
        if "LLVM_DIR_PATH" in os.environ:
            llvm_dir = os.environ["LLVM_DIR_PATH"]
        elif llvm_dir is None:
            msg = (
                "Failed to find a LLVM installation providing the file "
                "/usr/lib{32,64}/llvm-{VER}/lib/libclang.so.1. Make sure that "
                "you have installed the packages libclang1-{VER} and "
                "libc++-{VER}-dev, where {VER} refers to the desired "
                "Clang/LLVM version (e.g. 11). You may alternatively override "
                "the automatic search by specifying the LLVM_DIR_PATH "
                "(for the LLVM base directory) and/or LIBCLANG_PATH (if "
                "libclang is located at a nonstandard location) environment "
                "variables."
            )
            raise FileNotFoundError(msg)

        if "LIBCLANG_PATH" in os.environ:
            libclang_dir = os.environ["LIBCLANG_PATH"]
        else:
            libclang_dir = os.path.join(llvm_dir, "lib", "libclang.so.1")

        if not cindex.Config.loaded:
            cindex.Config.set_library_file(libclang_dir)
        cpp_dirs = []

        if "-stdlib=libc++" not in args:
            cpp_dirs.append(max(glob("/usr/include/c++/*"), default=None, key=folder_version))

            cpp_dirs.append(
                max(glob(f"/usr/include/{platform.machine()}-linux-gnu/c++/*"), default=None, key=folder_version)
            )
        else:
            cpp_dirs.append(os.path.join(llvm_dir, "include", "c++", "v1"))

        if "CLANG_INCLUDE_DIR" in os.environ:
            cpp_dirs.append(os.environ["CLANG_INCLUDE_DIR"])
        else:
            cpp_dirs.append(
                max(glob(os.path.join(llvm_dir, "lib", "clang", "*", "include")), default=None, key=folder_version)
            )

        cpp_dirs.append(f"/usr/include/{platform.machine()}-linux-gnu")
        cpp_dirs.append("/usr/include")

        # Capability to specify additional include directories manually
        if "CPP_INCLUDE_DIRS" in os.environ:
            cpp_dirs.extend([cpp_dir for cpp_dir in os.environ["CPP_INCLUDE_DIRS"].split() if os.path.exists(cpp_dir)])

        for cpp_dir in cpp_dirs:
            if cpp_dir is None:
                continue
            parameters.extend(["-isystem", cpp_dir])

    for item in args:
        if item.startswith("-"):
            parameters.append(item)
        else:
            filenames.append(item)

    if len(filenames) == 0:
        msg = "args parameter did not contain any filenames"
        raise NoFilenamesError(msg)

    return parameters, filenames


def extract_all(args):
    parameters, filenames = read_args(args)
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        results = executor.map(_extract_file, filenames, repeat(parameters))
        return [comment for output in results for comment in output]


def write_header(comments, out_file=sys.stdout):
    print(
        """/*
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
#define MKD_DOC6(n1, n2, n3, n4, n5, n6)                   mkd_doc_##n1##_##n2##_##n3##_##n4##_##n5##_##n6
#define MKD_DOC7(n1, n2, n3, n4, n5, n6, n7)               mkd_doc_##n1##_##n2##_##n3##_##n4##_##n5##_##n6##_##n7
#define DOC(...)                                           MKD_EXPAND(MKD_EXPAND(MKD_CAT2(MKD_DOC, MKD_VA_SIZE(__VA_ARGS__)))(__VA_ARGS__))

#if defined(__GNUG__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wunused-variable"
#endif
""",
        file=out_file,
    )

    # A suffixed name must not collide with a real symbol of that name, or with an earlier suffixed name.
    taken = {name for name, _, _ in comments}
    name_ctr = 1
    name_prev = None
    for name, _, comment in sorted(comments, key=lambda x: (x[0], x[1])):
        if name == name_prev:
            name_ctr += 1
            while f"{name_prev}_{name_ctr}" in taken:
                name_ctr += 1
            name = f"{name_prev}_{name_ctr}"
            taken.add(name)
        else:
            name_prev = name
            name_ctr = 1
        print(
            '\nstatic const char *{} ={}R"doc({})doc";'.format(name, "\n" if "\n" in comment else " ", comment),
            file=out_file,
        )

    print(
        """
#if defined(__GNUG__)
#pragma GCC diagnostic pop
#endif
""",
        file=out_file,
    )


def mkdoc(args, width, output=None):
    if width is not None:
        global docstring_width
        docstring_width = width
    comments = extract_all(args)

    if output:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
            with open(output, "w") as out_file:
                write_header(comments, out_file)
        except:
            # In the event of an error, don't leave a partially-written
            # output file.
            with contextlib.suppress(Exception):
                os.unlink(output)
            raise
    else:
        write_header(comments)
