import os
import argparse
import wsgiref.simple_server

from roundup.cgi.wsgi_handler import RequestDispatcher


def get_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('--site', default='site')
	default_port = int(os.environ.get('PORT', 8000))
	parser.add_argument('--port', type=int, default=default_port)
	return parser.parse_args()

def run():
	args = get_args()

	app = RequestDispatcher(args.site)
	httpd = wsgiref.simple_server.make_server('', args.port, app)
	print("Listening on port {port}...".format(**locals()))
	httpd.serve_forever()

if __name__ == '__main__':
	run()
