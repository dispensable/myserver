from functools import wraps
from json import dumps

from myframework.error import PluginAlreadyExistsException
from .plugin import Plugin


class JsonPlugin(Plugin):
    """ JSON Plugin transfer python dict to a JSON object. """
    def __init__(self, keyword='json'):
        self.keyword = keyword
        super(JsonPlugin, self).__init__('Json', 0.1)

    def setup(self, app):
        for json_plugin in app.plugins:
            if not isinstance(json_plugin, JsonPlugin):
                continue
            if json_plugin.keyword == self.keyword:
                raise PluginAlreadyExistsException(self)

    def __call__(self, callback, route):
        return self.apply(callback, route)

    def apply(self, callback, route):
        encoding = route.config.get('encoding') or 'utf-8'

        @wraps(callback)
        def wrapper(*args, **kwargs):
            result = callback(*args, **kwargs)
            if isinstance(result, dict):
                result = dumps(result)
                return result
            return callback(*args, **kwargs)

        return wrapper

    def close(self):
        pass