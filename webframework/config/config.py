# -*- coding:utf-8 -*-

from .clidoc import CLI_DOC
from docopt import docopt
from .validate import schema
from schema import SchemaError
import os.path
import sys
import traceback

__version__ = '0.1.0'


class Config(object):
    def __init__(self, argv=None):
        self.cli_doc = CLI_DOC
        self.settings = {}
        self.argv = argv
        self.default_conf = self.get_defualt_settings()

    def set(self, setting, value):
        if setting not in self.settings:
            raise AttributeError("No such configuration: {}".format(setting))
        self.settings[setting] = value

    def get(self, setting):
        if setting in self.settings:
            return self.settings[setting]
        raise AttributeError('No config item for {}'.format(setting))

    def get_config_from_cli(self):
        self.settings = docopt(self.cli_doc, argv=self.argv[1:], version=__version__)
        self.change_docopt_format()
        self.validate_and_save(self.settings)

    def validate_and_save(self, config):
        """ 验证cli数据并转化为python的数据结构 """
        try:
            data = schema.validate(config)
        except SchemaError as e:
            raise SchemaError(e)
        else:
            self.settings = data
            return data

    @staticmethod
    def get_default_config_file():
        config_path = os.path.join(os.path.dirname(os.getcwd()), 'config', 'default_conf.py')
        if os.path.exists(config_path):
            return config_path
        return None

    def change_docopt_format(self):
        """ 将docopt返回的字典键转为符合python变量名要求的格式"""
        settings = {}
        for key, value in self.settings.items():
            if '-' in key:
                key = key[2:].replace('-', '_')
            elif '<' in key or '>' in key:
                key = key[1:-1]
            settings[key] = value
        if settings:
            self.settings = settings

    def merge_cli_setting(self, cli_setting, config):
        cli_setting = self.get_change_from_cli(cli_setting)
        for key, value in cli_setting.items():
            config[key] = value
        self.validate_and_save(config)

    def get_change_from_cli(self, cli_setting):
        cli_config = {}
        for key, value in cli_setting.items():
            if self.default_conf[key] != value:
                cli_config[key] = value
        return cli_config

    def get_defualt_settings(self):
        filename = self.get_default_config_file()
        if filename:
            return self.get_settings_from_file(filename)
        return None

    def override_config(self, config):
        self.settings.update(config)

    @staticmethod
    def get_settings_from_file(filename):
        if not os.path.exists(filename):
            raise RuntimeError('{} not exists'.format(filename))

        cfg = {
            "__builtins__": __builtins__,
            "__name__": "__config__",
            "__file__": filename,
            "__doc__": None,
            "__package__": None
        }

        try:
            exec(open(filename).read(), cfg, cfg)
        except Exception:
            print("Can't read config file: {}".format(filename), file=sys.stderr)
            traceback.print_exc()
            sys.stderr.flush()
            sys.exit(1)
        del cfg['__builtins__']
        return cfg

