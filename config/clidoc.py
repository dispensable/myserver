from docopt import docopt
from ..utils import __version__

CLI_DOC = """Myframwork.
Usage:
myframework [options] package.module:app

Options:
  -h, --help            show this help message and exit
  --version             show version number.
  -b ADDRESS, --bind=ADDRESS
                        bind socket to ADDRESS.
  -s SERVER, --server=SERVER
                        use SERVER as backend.
  -p PLUGIN, --plugin=PLUGIN
                        install additional plugin/s.
  -c FILE, --conf=FILE  load config values from FILE.
  -C NAME=VALUE, --param=NAME=VALUE
                        override config values.
  --debug               start server in debug mode. [default: False]
  --reload              auto-reload on file changes. [default: True]"""


if __name__ == '__main__':
    arguments = docopt(CLI_DOC, version=__version__)
    print(arguments)
