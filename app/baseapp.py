# _*_ coding:utf-8 _*_

import sys
from config.config import Config
from watcher import Watcher
import os.path
import traceback


class BaseApp(object):
    """ A layer between server app and framwork app.
    Load some config before server start"""
    def __init__(self, argv):
        self.callable = None
        self.config = None
        self.logger = None
        self.argv = argv
        self.load_config()

    def load_config(self):
        try:
            self.load_deafult_config()
            self.load_app_config()
        except Exception as e:
            print("ERROR: when loading config:\n{}".format(str(e)), file=sys.stderr)
            sys.stderr.flush()
            sys.exit(1)

    def load_deafult_config(self):
        self.config = Config(self.argv)

    def load_app_config(self):
        """ load app config to convert default app """
        raise NotImplementedError

    def load(self):
        """ load app before server boot"""
        raise NotImplementedError

    def reload(self):
        self.load_config()

    def app_init(self):
        """ initialize the app """
        raise NotImplementedError

    def wsgi(self):
        if self.callable is None:
            self.callable = self.load()
        return self.callable

    def run(self):
        try:
            Watcher(self).run()
        except RuntimeError as e:
            print("ERROR: when start running server watcher:\n{}".format(str(e)), file=sys.stderr)
            sys.stderr.flush()
            sys.exit(1)


class App(BaseApp):

    def load_all_config(self):
        # 解析命令行配置
        self.config.get_config_from_cli()

        # 读取配置文件
        filename = self.config.settings['config']

        if filename:
            config = self.config.get_settings_from_file(filename)
            self.config.merge_cli_setting(self.config.settings, config)
        else:
            self.config.merge_cli_setting(self.config.settings, self.config.default_conf)

    def run(self):
        self.load_all_config()
        print(self.config.settings)
        super(App, self).run()
