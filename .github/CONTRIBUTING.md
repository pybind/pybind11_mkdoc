
# Building from source

If you want to work on this repository, the standard recipe is shown below,
with `flit` being used for the editable install, because adding a unified
interface for editable installs to PEP 517 is still an open topic.

```bash
python3 -m venv venv
. venv/bin/activate
pip install flit
flit install --symlink
```

Other than this, using `pip` and
[`python-build`](https://python-build.readthedocs.io/en/latest/) should work as
expected, though `flit` does also have a nice [command line
interface](https://flit.readthedocs.io/en/latest/cmdline.html).
