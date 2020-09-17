from .mkdoc_lib import mkdoc
import sys


if __name__ == "__main__":
    mkdoc_out = None
    mkdoc_help = False
    mkdoc_args = []

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]

        if arg == '-h':
            mkdoc_help = True
        elif arg == '-o':
            mkdoc_out = sys.argv[i + 1]
            i += 1 # Skip next
        elif arg.startswith('-o'):
            mkdoc_out = arg[2:]
        elif arg == '-I':
            # Concatenate include directive and path
            mkdoc_args.append(arg + sys.argv[i + 1])
            i += 1 # Skip next
        else:
            mkdoc_args.append(arg)
        i += 1

    if len(mkdoc_args) == 0 or mkdoc_help:
        print("""Syntax: python -m pybind11_mkdoc [options] .. list of headers files ..

This tool processes a sequence of C/C++ headers and extracts comments for use
in pybind11 binding code.

Options:

  -h                Display this help text

  -o <filename>     Write to the specified filename (default: use stdout)

  -I <path>         Specify an include directory

  -Dkey=value       Specify a compiler definition

(Other compiler flags that Clang understands can also be supplied)""")
    else:
        mkdoc(mkdoc_args, mkdoc_out)
