import os
import stat
import mimetypes
import urlparse 

from future_builtins import map

from dulwich.objects import Commit, Blob

from klaus.nano import HttpError
from klaus.repo import Repo
from klaus import utils

def get_repo(app, name):
    try:
        return Repo(name, app.repos[name])
    except KeyError:
        raise HttpError(404, 'No repository named "%s"' % name)

def query_string_to_dict(query_string):
    """ Transforms a POST/GET string into a Python dict """
    return dict((k, v[0]) for k, v in urlparse.parse_qs(query_string).iteritems())

__routes__ = {}

def install(app):
    for pattern,cls in __routes__.iteritems():
        app.route(pattern)(cls)

def route(pattern, name=None):
    def decorator(cls):
        global __routes__
        cls.__name__ = name or cls.__name__.lower()
        __routes__[pattern] = cls
        return cls
    return decorator

def subpaths(path):
    """
    Yields a `(last part, subpath)` tuple for all possible sub-paths of `path`.

    >>> list(subpaths("foo/bar/spam"))
    [('foo', 'foo'), ('bar', 'foo/bar'), ('spam', 'foo/bar/spam')]
    """
    seen = []
    for part in path.split('/'):
        seen.append(part)
        yield part, '/'.join(seen)
        
class BaseView(dict):
    
    def __init__(self, app, env):
        self.app = app
        dict.__init__(self)
        self['environ'] = env
        self.GET = query_string_to_dict(env.get('QUERY_STRING', ''))
        
    def __call__(self):
        self.view()
        return self
        
    def direct_response(self, *args):
        raise self.app.error_exc(*args)

@route('/', 'repo_list')
class RepoList(BaseView):
    """ Shows a list of all repos and can be sorted by last update. """
    def view(self):
        self['repos'] = repos = []
        for name in self.app.repos.iterkeys():
            repo = get_repo(self.app, name)            
            refs = []
            try:
                refs = [repo[ref] for ref in repo.get_refs()]
            except Exception,e:
                raise self.app.error_exc(e)
            if refs:
                refs.sort(key=lambda obj:getattr(obj, 'commit_time', None),
                          reverse=True)            
                repos.append((name, refs[0].commit_time))
        if 'by-last-update' in self.GET:
            repos.sort(key=lambda x: x[1], reverse=True)
        else:
            repos.sort(key=lambda x: x[0])

class BaseRepoView(BaseView):
    def __init__(self, app, env, repo, commit_id, path=None):        
        super(BaseRepoView, self).__init__(app, env)
        self['repo'] = repo = get_repo(self.app,repo)
        self['commit_id'] = commit_id
        self['commit'], isbranch = self.get_commit(repo, commit_id)
        self['branch'] = commit_id if isbranch else 'master'
        self['branches'] = repo.get_branch_names(exclude=[commit_id])
        self['path'] = path
        if path:
            self['subpaths'] = list(subpaths(path))
        self['build_url'] = self.build_url

    def get_commit(self, repo, id):
        try:
            commit, isbranch = repo.get_branch_or_commit(id)
            if not isinstance(commit, Commit):
                raise KeyError
        except KeyError:
            raise HttpError(404, '"%s" has no commit "%s"' % (repo.name, id))
        return commit, isbranch

    def build_url(self, view=None, **kwargs):
        """ Builds url relative to the current repo + commit """
        if view is None:
            view = self.__class__.__name__
        default_kwargs = {
            'repo': self['repo'].name,
            'commit_id': self['commit_id']
        }
        if view == 'history' and kwargs.get('path') is None:
            kwargs['path'] = ''
        return self.app.build_url(view, **dict(default_kwargs, **kwargs))


class TreeViewMixin(object):
    def view(self):
        self['tree'] = self.listdir()

    def listdir(self):
        """
        Returns a list of directories and files in the current path of the
        selected commit
        """
        dirs, files = [], []
        tree, root = self.get_tree()
        for entry in tree.iteritems():
            name, entry = entry.path, entry.in_path(root)
            if entry.mode & stat.S_IFDIR:
                dirs.append((name.lower(), name, entry.path))
            else:
                files.append((name.lower(), name, entry.path))
        files.sort()
        dirs.sort()
        if root:
            dirs.insert(0, (None, '..', os.path.split(root)[0]))
        return {'dirs' : dirs, 'files' : files}

    def get_tree(self):
        """ Gets the Git tree of the selected commit and path """
        root = self['path']
        tree = self['repo'].get_tree(self['commit'], root)
        if isinstance(tree, Blob):
            root = os.path.split(root)[0]
            tree = self['repo'].get_tree(self['commit'], root)
        return tree, root

@route('/:repo:/tree/:commit_id:/(?P<path>.*)', 'history')
class TreeView(TreeViewMixin, BaseRepoView):
    """
    Shows a list of files/directories for the current path as well as all
    commit history for that path in a paginated form.
    """
    def view(self):
        super(TreeView, self).view()
        try:
            page = int(self.GET.get('page'))
        except (TypeError, ValueError):
            page = 0

        self['page'] = page

        if page:
            self['history_length'] = 30
            self['skip'] = (self['page']-1) * 30 + 10
            if page > 7:
                self['previous_pages'] = [0, 1, 2, None] + range(page)[-3:]
            else:
                self['previous_pages'] = xrange(page)
        else:
            self['history_length'] = 10
            self['skip'] = 0

class BaseBlobView(BaseRepoView):
    def view(self):
        self['blob'] = self['repo'].get_tree(self['commit'], self['path'])
        self['directory'], self['filename'] = os.path.split(self['path'].strip('/'))

@route('/:repo:/blob/:commit_id:/(?P<path>.*)', 'view_blob')
class BlobView(BaseBlobView, TreeViewMixin):
    """ Shows a single file, syntax highlighted """
    def view(self):
        BaseBlobView.view(self)
        TreeViewMixin.view(self)
        self['raw_url'] = self.build_url('raw_blob', path=self['path'])
        self['too_large'] = sum(map(len, self['blob'].chunked)) > 100*1024

@route('/:repo:/raw/:commit_id:/(?P<path>.*)', 'raw_blob')
class RawBlob(BaseBlobView):
    """
    Shows a single file in raw form
    (as if it were a normal filesystem file served through a static file server)
    """
    def view(self):
        super(RawBlob, self).view()
        mime, encoding = self.get_mimetype_and_encoding()
        headers = {'Content-Type': mime}
        if encoding:
            headers['Content-Encoding'] = encoding
        body = self['blob'].chunked
        if len(body) == 1 and not body[0]:
            body = []
        self.direct_response('200 yo', headers, body)

    def get_mimetype_and_encoding(self):
        if utils.guess_is_binary(self['blob'].chunked):
            mime, encoding = mimetypes.guess_type(self['filename'])
            if mime is None:
                mime = 'appliication/octet-stream'
            return mime, encoding
        else:
            return 'text/plain', 'utf-8'


@route('/:repo:/commit/:commit_id:/', 'view_commit')
class CommitView(BaseRepoView):
    """ Shows a single commit diff """
    def view(self):
        pass

@route('/static/(?P<path>.+)', 'static')
class StaticFilesView(BaseView):
    """
    Serves assets (everything under /static/).

    Don't use this in production! Use a static file server instead.
    """
    def __init__(self, app, env, path):
        self['path'] = path
        super(StaticFilesView, self).__init__(app, env)

    def view(self):
        import klaus.static
        static_path = os.path.dirname(klaus.static.__file__)
        relpath = os.path.join(static_path, self['path'])
        if os.path.isfile(relpath):
            self.direct_response(open(relpath))
        else:
            raise HttpError(404, 'Not Found')