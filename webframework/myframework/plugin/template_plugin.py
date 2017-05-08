import os
from functools import wraps

from myframework.error import PluginAlreadyExistsException
from .plugin import Plugin


class Template:
    """ return template format """
    def __init__(self, temp_name, plugin_name, temp_dir, **kwargs):
        self.temp_name = temp_name
        self.name = plugin_name
        self.dir = temp_dir
        self.kwargs = kwargs


class TemplatePlugin(Plugin):
    def __init__(self, name, template_dir=os.getcwd()+'/templates', api_version=0.1):
        self.template_dir = template_dir
        super(TemplatePlugin, self).__init__(name, api_version)

    def setup(self, app):
        """ called when install plugin to the app
            :param app: Myframwork instance
         """
        for p in app.plugins.copy():
            if isinstance(p, TemplatePlugin) and p.template_dir == self.template_dir:
                raise PluginAlreadyExistsException(self)

    def __call__(self, callback, route):
        """ Been called to apply directly to each route callback. """
        raise NotImplementedError

    def apply(self, callback, route):
        raise NotImplementedError

    def close(self):
        """ been called when uninstall this plugin """
        raise NotImplementedError


class MakoTemplatePlugin(TemplatePlugin):
    def __init__(self):
        from mako.lookup import TemplateLookup
        self.TemplateLookup = TemplateLookup
        super(MakoTemplatePlugin, self).__init__('MaKo Template Plugin', api_version=0.1)

    def __call__(self, callback, route):
        self.apply(callback, route)

    def apply(self, callback, route):
        config = route.config

        @wraps(callback)
        def wrapper(*args, **kwargs):
            result = callback(*args, **kwargs)
            if isinstance(result, Template):
                lookup = self.TemplateLookup(directories=result.dir, **config)
                mytemplate = lookup.get_template(result.temp_name)
                return mytemplate.render(**result.kwargs)
            return callback(*args, **kwargs)
        return wrapper

    def close(self):
        pass
