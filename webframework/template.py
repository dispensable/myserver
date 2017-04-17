class TemplateEngine(object):
    def __call__(self, path, model):
        raise NotImplementedError('Need template engine')


class Jinja2TemplateEngine(TemplateEngine):
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        pass