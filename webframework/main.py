# -*- coding:utf-8 -*-
import sys
import os
from config.config import Config
from wsgiref import simple_server


class BaseApp:
    def __init__(self, argv):
        self.argv = argv
        self.cfg = Config(self.argv)

    def chdir(self, path):
        os.chdir(path)
        sys.path.insert(0, path)

    def load_all_config(self):
        # 解析命令行配置
        self.cfg.get_config_from_cli()

        # 读取配置文件
        filename = self.cfg.settings.get('conf')

        if filename:
            config = self.cfg.get_settings_from_file(filename)
            self.cfg.merge_cli_setting(self.cfg.settings, config)
        else:
            self.cfg.merge_cli_setting(self.cfg.settings, self.cfg.default_conf)

    def load_app(self):
        cfg = self.cfg

        try:
            path = cfg.get('chdir')
        except AttributeError:
            path = os.getcwd()
        else:
            if not os.path.exists(path):
                path = os.getcwd()

        self.chdir(path)
        package_app = cfg.get('package.module:app')
        package_module, app = package_app.split(':')

        try:
            exec('from {package_module}'
                 ' import {app}'.format(package_module=package_module, app=app))
        except ImportError:
            raise

        return eval(app)

    def run(self):
        self.load_all_config()
        my_framework_app = self.load_app()
        my_framework_app.load_config(self.cfg)
        host_port = self.cfg.get('bind')
        host, port = host_port.split(':')
        server = simple_server.make_server(host, int(port), my_framework_app)
        server.serve_forever()


if __name__ == '__main__':
    BaseApp(sys.argv).run()
