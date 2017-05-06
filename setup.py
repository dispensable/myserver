try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

from myserver.version import __version__

setup(
    name='myserver',
    version=__version__,
    packages=find_packages(),
    entry_points={
        'console_scripts': ['myserver=myserver.main:run']
        },
)