try:
    from bjoern import run      
except ImportError:
    from wsgiref.simple_server import make_server
    def run(app, host, port):
        make_server(host, port, app).serve_forever()
