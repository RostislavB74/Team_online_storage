import pathlib
import tomllib

from .celery import app as celery_app

__all__ = ("celery_app",)

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("teamchallenge-1444")
except PackageNotFoundError:  # pragma: no cover
    default_version = "0.0.1.dev"
    try:
        with pathlib.Path(__file__).parent.parent.parent.joinpath('pyproject.toml').open(mode='rb') as pyproject:
            __version__ = tomllib.load(pyproject).get('tool',{}).get('poetry',{}).get('version', default_version)
    except Exception:  # pragma: no cover
        __version__ = default_version

    __version__ = str(__version__)