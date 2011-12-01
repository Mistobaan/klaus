app = None

import logging
import os
_logger = logging.getLogger()

def createApp(repositories):
    from klaus import application
    from klaus import templates
    from klaus import views
    templates = os.path.dirname(templates.__file__)
    # KLAUS_REPOS=/foo/bar/,/spam/ --> {'bar': '/foo/bar/', 'spam': '/spam/'}
    repos = dict((repo.rstrip(os.sep).split(os.sep)[-1], repo)
                        for repo in repositories) 
    app = application.KlausApplication(templates,repos,debug=True, default_content_type='text/html')

    views.install(app)
    return app

from klaus import server

run = server.run