from functools import wraps

from klaus.nano import NanoApplication
from klaus import jinjaenv

class Response(Exception):
    pass
    
class KlausApplication(NanoApplication):
    error_exc = Response
    version = "1.0"
    
    def __init__(self, templates, repos, *args, **kwargs):
        super(KlausApplication, self).__init__(*args, **kwargs)
        self.jinja_env = jinjaenv.createEnv(self.version, templates, self.build_url )
        self.repos = repos
         
    def route(self, pattern):
        """
        Extends `NanoApplication.route` by multiple features:

        - Overrides the WSGI `HTTP_HOST` by `self.custom_host` (if set)
        - Tries to use the keyword arguments returned by the view function
          to render the template called `<class>.html` (<class> being the
          name of `self`'s class). Raising `Response` can be used to skip
          this behaviour, directly returning information to Nano.
        """
        super_decorator = super(KlausApplication, self).route(pattern)
        def decorator(callback):
            @wraps(callback)
            def wrapper(env, **kwargs):
                if hasattr(self, 'custom_host'):
                    env['HTTP_HOST'] = self.custom_host
                try:
                    return self.render_template(callback.__name__ + '.html',
                                                **(callback(self, env, **kwargs)()))
                except self.error_exc as e:
                    if len(e.args) == 1:
                        return e.args[0]
                    return e.args
            return super_decorator(wrapper)
        return decorator

    def render_template(self, template_name, **kwargs):
        return self.jinja_env.get_template(template_name).render(**kwargs)
