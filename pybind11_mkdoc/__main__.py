import argparse
from .mkdoc_lib import mkdoc


def main():
    parser = argparse.ArgumentParser(description="Process header file comments and make pybind11 compatible doc files")
    parser.add_argument("-o", "--output", help="An output file to produce (stdout default)")
    parser.add_argument("args", nargs="+", help="Files to run on")
    args = parser.parse_args()

    mkdoc(args.args, args.output)


if __name__ == "__main__":
    main()
