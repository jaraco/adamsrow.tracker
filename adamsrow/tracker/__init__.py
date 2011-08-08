from roundup.cgi import wsgi_handler

def init():
	"""
	Initialize the WSGI app
	"""
	tracker_home = 'tracker'
	return wsgi_handler.RequestDispatcher(tracker_home)
