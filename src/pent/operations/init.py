import pathlib
import subprocess
import sys

import click

from pent import _pipenv, checks, envs


def _supports_venv(executable):
    version = _pipenv.get_python_version(executable)
    major, minor, _ = version.split('.', 2)

    # venv is only usable after 3.6, with --prompt added.
    if (int(major), int(minor)) >= (3, 6):
        return True
    return False


def _find_venv_python(venv):
    for python in envs.iter_python(venv):
        return python
    raise ValueError(f'no python found in environment')


@checks.pipfile_required
def init(python, prompt, clear):
    project_root = pathlib.Path(_pipenv.get_project().project_directory)
    venv_path = project_root.joinpath('.venv')
    args = [str(venv_path)]

    if venv_path.exists():
        if not clear:
            click.echo(f'Environment exists at {venv_path}', err=True)
            return
        args.append('--clear')

    if not prompt:
        prompt = project_root.name
    args.extend(['--prompt', prompt])

    uses_venv = _supports_venv(python)
    backend = 'venv' if uses_venv else 'virtualenv'
    click.echo(f'Creating new {backend} at {venv_path}', err=True)
    click.echo(f'Using {python}', err=True)

    if uses_venv:
        subprocess.check_call([python, '-m', 'venv'] + args)
    else:
        subprocess.check_call([
            sys.executable, '-m', 'virtualenv',
            '--quiet', '--python', python,
        ] + args)

    click.echo(f'Making sure pip and Setuptools are up-to-date', err=True)
    subprocess.check_call([
        str(_find_venv_python(venv_path)), '-m', 'pip', 'install',
        '--upgrade', '--disable-pip-version-check', '--quiet',
        'setuptools', 'pip',
    ])
