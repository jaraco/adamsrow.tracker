import os
import wsgiref.simple_server

from roundup.cgi.wsgi_handler import RequestDispatcher

tracker_home = '.'
app = RequestDispatcher(tracker_home)
port = int(os.environ.get('PORT', 8000))
httpd = wsgiref.simple_server.make_server('', port, app)
print("Listening on port {port}...".format(**locals()))
httpd.serve_forever()
