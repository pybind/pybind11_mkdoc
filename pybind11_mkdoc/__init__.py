"""
This is a package for building pybind11 docstrings from C++ header comments.

(Docs WIP).
"""


import argparse
import os
import re
import shlex
import sys

from .mkdoc_lib import mkdoc


__version__ = "2.6.1.dev1"


def _append_include_dir(args: list, include_dir: str, verbose: bool = True):
    """
    Add an include directory to an argument list (if it exists).

    Parameters
    ----------

    args: list
        The list to append the include directory to.

    include_dir: str
        The include directory to append.

    verbose: bool
        Whether to print a warning for non-existing directories.
    """

    if os.path.isdir(include_dir):
        args.append(f"-I{shlex.quote(include_dir)}")
    elif verbose:
        print(f"Include directoy '{shlex.quote(include_dir)}' does not exist!")


def _append_definition(args: list, definition: str, verbose: bool = True):
    """
    Add a compiler definition to an argument list.
    
    The definition is expected to be given in the format '<macro>=<value>',
    which will define <macro> to <value> (or 1 if <value> is omitted).

    Parameters
    ----------

    args: list
        The list to append the definition to.

    definition: str
        The definition to append.

    verbose: bool
        Whether to print a warning for invalid definition strings.
    """

    try:
        macro, value = definition.strip().split('=')
        macro = shlex.quote(macro.strip())
        value = shlex.quote(value.strip()) if value else '1'

        args.append(f"-D{macro}={value}")
    except ValueError as exc:
        # most likely means there was no '=' given
        # check if argument is valid identifier
        if re.search(r'^[A-Za-z_][A-Za-z0-9_]*', definition):
            args.append(f"-D{definition}")
        else:
            print(f"Failed to parse definition: {shlex.quote(definition)}")
    except:
        print(f"Failed to parse definition: {shlex.quote(definition)}")
    


def main():
    """
    Entry point for the `pybind11_mkdoc` console script.

    Parses the  commandline arguments given to the console script and passes them on to `mkdoc`.
    """

    parser = argparse.ArgumentParser(
            description="Processes a sequence of C/C++ headers and extracts comments for use in pybind11 binding code.",
            epilog="(Other compiler flags that CLang understands can also be supplied)",
            allow_abbrev=False
            )
    
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")
    
    parser.add_argument("-o", "--output", action="store", type=str, dest="output", metavar="<file>",
                        help="Write to the specified file (default: use stdout).")

    parser.add_argument("-w", "--width", action="store", type=int, dest="width", metavar="<width>",
                        help="Specify docstring width before wrapping.")

    parser.add_argument("-I", action="append", type=str, dest="include_dirs", metavar="<dir>",
                        help="Specify an directory to add to the list of include search paths.")

    parser.add_argument("-D", action="append", type=str, metavar="<macro>=<value>", dest="definitions",
                        help="Specify a compiler definition, i.e. define <macro> to <value> (or 1 if <value> omitted).")

    parser.add_argument("header", type=str, nargs='+', help="A header file to process.")

    [parsed_args, unparsed_args] = parser.parse_known_args()

    mkdoc_args = []
    mkdoc_out = parsed_args.output
    docstring_width = parsed_args.width

    if parsed_args.include_dirs is not None:
        for include_dir in parsed_args.include_dirs:
            _append_include_dir(mkdoc_args, include_dir)

    if parsed_args.definitions is not None:
        for definition in parsed_args.definitions:
            _append_definition(mkdoc_args, definition)

    for arg in unparsed_args:
        if arg.startswith("-I"):
            _append_include_dir(mkdoc_args, arg[2:])
        elif arg.startswith("-D"):
            _append_definition(mkdoc_args, arg[2:])
        else:
            # append argument as is and hope for the best
            mkdoc_args.append(shlex.quote(arg))

    for header in parsed_args.header:
        mkdoc_args.append(shlex.quote(header))

    mkdoc(mkdoc_args, docstring_width, mkdoc_out)

    return 0
