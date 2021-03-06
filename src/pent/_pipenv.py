"""A wrapper to make Pipenv behave well as a library.
"""

import functools
import importlib
import os
import pathlib

# Hack to work around Pipenv's annoying import-time side effect of changing
# the current working directory to the project root.
cwd = os.getcwd()
from pipenv import core, shells, utils  # noqa
os.chdir(cwd)


@functools.lru_cache(maxsize=1)
def get_project():
    return core.project


class PythonVersionNotFound(ValueError):
    pass


def get_python_version(executable):
    version = utils.python_version(str(executable))
    if not version:
        raise PythonVersionNotFound(executable)
    return version


def get_venv_path():
    return pathlib.Path(get_project().pipfile_location).with_name('.venv')


def import_patched(path):
    """Get a Pipenv submodule.

    This is done to make sure the above cwd hack is applied before importing.
    """
    return importlib.import_module(f'pipenv.patched.{path}')
