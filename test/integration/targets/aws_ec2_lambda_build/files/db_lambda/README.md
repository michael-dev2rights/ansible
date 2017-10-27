This directory contains information for building the zip file(s) used in this task.  This
is included so that you can rebuild them, however they must be included as pre-built in
the source code directory since the test case is expected to run on platforms that are not
able to actually build the lambda deployment file.

N.B. to get this to build correctly you have to run a python3 venv inside a tox venv
whilst ignoring the pip provided by the external tox venv.  This is probably practically
impossible without fixing a series of bugs in pip.

See for example:  https://github.com/pypa/virtualenv/issues/596
(PIP people refuse to fix)
