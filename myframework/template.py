from mako.lookup import TemplateLookup
import os


class TemplateEngine(object):
    def __call__(self, path, model):
        raise NotImplementedError('Need template engine')


class Jinja2TemplateEngine(TemplateEngine):
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        pass


class MakoTemplateEngine(TemplateEngine):
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        pass


def render_template(template_name, directory=os.getcwd() + '/templates', **kwargs):
    print(directory)
    lookup = TemplateLookup(directories=directory)
    mytemplate = lookup.get_template(template_name)
    return mytemplate.render(**kwargs)
