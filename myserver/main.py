# -*- coding:utf-8 -*-

import os
import sys

from myserver.app.baseapp import App


class MainApp(App):

    def init(self):
        self.app_uri = (self.config.settings['module'], self.config.settings['app'])
        return self.app_uri

    def chdir(self, path):
        os.chdir(path)
        sys.path.insert(0, path)

    def load_app_config(self):
        pass

    def load_wsgiapp(self):
        cfg = self.config
        try:
            path = cfg.get('chdir')
        except AttributeError:
            path = os.getcwd()
        else:
            if not os.path.exists(path):
                path = os.getcwd()

        self.chdir(path)
        package_module, app = self.init()

        try:
            exec('from {package_module}'
                 ' import {app}'.format(package_module=package_module, app=app))
        except ImportError:
            raise


        return eval(app)

    def load(self):
        return self.load_wsgiapp()


def run():
    MainApp(sys.argv).run()

if __name__ == '__main__':
    run()
