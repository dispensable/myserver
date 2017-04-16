# -*- coding:utf-8 -*-

from baseapp import App
import sys
import os
from wsgiapp import wsgi_app


class TestApp(App):

    def init(self):
        self.app_uri = (self.config.settings['module'], self.config.settings['app'])

    def chdir(self):
        os.chdir(self.config.settings['chdir'])
        sys.path.append(0, self.config.settings['chdir'])

    def load_app_config(self):
        pass

    def load_wsgiapp(self):
        self.chdir()
        module, app = self.app_uri
        try:
            __import__(module)
        except ImportError:
            raise
        mod = sys.modules[module]

        try:
            app = eval(app, vars(mod))
        except NameError:
            raise ImportError("can't find app {}".format(app))

        if app is None:
            raise ImportError("can't find app, app is NONE")

        if not callable(app):
            raise ImportError("wsgi app must be callable")

        return app

    def load(self):
        return wsgi_app

def run():
    TestApp(sys.argv).run()

if __name__ == '__main__':
    run()