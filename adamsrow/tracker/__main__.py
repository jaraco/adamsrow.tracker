from roundup.cgi.wsgi_handler import RequestDispatcher
import wsgiref.simple_server

tracker_home = './Adams Row Tracker'
app = RequestDispatcher(tracker_home)
httpd = wsgiref.simple_server.make_server('', 8000, app)
print("Listening on port 8000....")
httpd.serve_forever()
