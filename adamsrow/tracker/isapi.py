from __future__ import absolute_import, print_function

"""
Things to remember when deploying an isapi_wsgi app:
 - easy_install munges permissions on zip eggs (the easiest solution is to just install them with -Z)
 - any dependency that's installed in a user folder (i.e. setup develop) will probably not work due to insufficient permissions
"""

import sys
import os
import traceback

import isapi_wsgi
import isapi.install

if hasattr(sys, "isapidllhandle"):
	import win32traceutil

def setup_environment(entry_file):
	"""
	Set up the ISAPI environment. <entry_file> should be the
	script/dll that is the entry point for the application.
	"""
	global appdir
	appdir = os.path.dirname(entry_file)
	egg_cache = os.path.join(appdir, 'egg-tmp')
	if not os.path.exists(egg_cache):
		os.makedirs(egg_cache)
		# todo: make sure NETWORK_SERVICE has write permission
	os.environ['PYTHON_EGG_CACHE'] = egg_cache
	os.chdir(appdir)

def setup_application():
	import adamsrow.tracker
	return adamsrow.tracker.init()

def factory():
	"The entry point for when the ISAPIDLL is triggered"
	try:
		return isapi_wsgi.ISAPISimpleHandler(setup_application())
	except:
		print("Traceback occurred starting up the application")
		traceback.print_exc()
		f = open(os.path.join(appdir, 'critical error.txt'), 'w')
		traceback.print_exc(file=f)
		f.close()

def handle_command_line():
	"Install or remove the extension to the virtual directory"
	params = isapi.install.ISAPIParameters()
	# Setup the virtual directories - this is a list of directories our
	# extension uses - in this case only 1.
	# Each extension has a "script map" - this is the mapping of ISAPI
	# extensions.
	sm = [
		isapi.install.ScriptMapParams(Extension="*", Flags=0)
	]
	vd = isapi.install.VirtualDirParameters(
		Server="Adams Row Tracker",
		Name="/",
		Description = "Adams Row Tracker",
		ScriptMaps = sm,
		ScriptMapUpdate = "end",
		)
	params.VirtualDirs = [vd]
	isapi.install.HandleCommandLine(params)
