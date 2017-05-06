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
    install_requires=['docopt>=0.6.2', 'inotify>=0.2.8', 'Mako>=1.0.6',
                      'pysendfile>=2.0.1', 'schema>=0.6.5', 'setproctitle>=1.1.10'],

    # metadata for upload to PyPI
    author="dispensable",
    author_email="sunsetmask@gmail.com",
    description="A pre-forked unix http web server",
    license="",
    keywords="http server",
    url="https://dispensable.github.io/myserver/",
)
