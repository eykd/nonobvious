# -*- coding: utf-8 -*-
"""pavement.py -- paver tasks for managing the nonobvious project.
"""
from paver.easy import task, sh


@task
def test():
    """Run the test suite w/ nosetests, with coverage and pretty colors.
    """
    sh(" ".join([
        "bin/nosetests",
        "-i",
        "'^(it|ensure|must|should|deve|specs?|examples?)'",
        "-i",
        "'(specs?|examples?|exemplos?)(.py)?$'",
        "--with-spec",
        "--spec-color",
        "--with-coverage",
        "--cover-package=nonobvious",
        "--nocapture",
    ]))


@task
def dev():
    """Set up the development environment.
    """
    sh("virtualenv .")
    sh("bin/pip install -r dev-requirements.txt")
