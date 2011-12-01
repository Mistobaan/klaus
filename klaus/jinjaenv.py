from klaus import utils
from pygments import highlight
from pygments.lexers import get_lexer_for_filename, get_lexer_by_name, \
                            guess_lexer, ClassNotFound
from pygments.formatters import HtmlFormatter
from jinja2 import Environment, FileSystemLoader

from functools import partial 

def pygmentize(formatter, code, filename=None, language=None):
    if language:
        lexer = get_lexer_by_name(language)
    else:
        try:
            lexer = get_lexer_for_filename(filename)
        except ClassNotFound:
            lexer = guess_lexer(code)
    return highlight(code, lexer, formatter)

def createEnv(version, templates, build_url):
    jinja_env = Environment(loader=FileSystemLoader(templates),
                                     extensions=['jinja2.ext.autoescape'],
                                     autoescape=True)
    pygments_formatter = HtmlFormatter(linenos=True)        
    jinja_env.globals['build_url'] = build_url
    jinja_env.globals['KLAUS_VERSION'] = version
    jinja_env.filters['u'] = utils.force_unicode
    jinja_env.filters['timesince'] = utils.timesince
    jinja_env.filters['shorten_sha1'] = utils.shorten_sha1
    jinja_env.filters['shorten_message'] = lambda msg: msg.split('\n')[0]
    jinja_env.filters['pygmentize'] = partial(pygmentize,pygments_formatter)
    jinja_env.filters['is_binary'] = utils.guess_is_binary
    jinja_env.filters['is_image'] = utils.guess_is_image
    jinja_env.filters['shorten_author'] = utils.extract_author_name
    
    return jinja_env      

