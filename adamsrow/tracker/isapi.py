from __future__ import absolute_import, print_function

"""
Things to remember when deploying an isapi_wsgi app:
	- easy_install munges permissions on zip eggs (the easiest solution is to
		just install them with -Z)
	- any dependency that's installed in a user folder (i.e. setup develop)
		will probably not work due to insufficient permissions
"""

import sys
import os
import traceback
import subprocess
import importlib
from textwrap import dedent

import isapi_wsgi
import isapi.install
from roundup.cgi import wsgi_handler

if hasattr(sys, "isapidllhandle"):
	importlib.import_module('win32traceutil')

appdir = None

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
	tracker_home = appdir
	return wsgi_handler.RequestDispatcher(tracker_home)

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

def create_site():
	root = r'C:\Inetpub\Adams Row Tracker'
	if not os.path.isdir(root):
		os.path.makedirs(root)
	create_iis_site(root)
	set_permissions()
	script = os.path.join(root, 'tracker.py')
	open(script, 'w').write(dedent("""
		from adamsrow.tracker.isapi import (
			factory as __ExtensionFactory__,
			handle_command_line, setup_environment,
		)
		setup_environment(__file__)
		if __name__ == '__main__': handle_command_line()
		"""))
	subprocess.check_call([sys.executable, script, 'install'])
	print("Now create site using 'roundup-admin install' and edit "
		"the config, or copy a previous instance.")
	print("Also install the mail checker task")

def appcmd(cmd, **kwargs):
	if isinstance(cmd, basestring):
		cmd = cmd.split()
	args = [
		'/{key}:{value}'.format(**vars())
		for key, value in kwargs.items()
	]
	return subprocess.check_call([
		r'\Windows\System32\InetSrv\appcmd.exe',
		] + cmd + args)

def create_iis_site(root):
	appcmd('add site',
		id = 4,
		name = 'Adams Row Tracker',
		physicalPath = root,
		bindings = 'http/*:80:tracker.adamsrowcondo.org',
	)
	appcmd('add apppool', name="Adams Row Tracker")
	appcmd(['set', 'app', 'Adams Row Tracker/'],
		applicationPool="Adams Row Tracker")

def set_permissions(root):
	subprocess.check_call([
		'icacls',
		root,
		'/grant',
		'IIS AppPool\Adams Row Tracker:(OI)(CI)(IO)(F)',
	])
	subprocess.check_call([
		'icacls',
		root,
		'/grant',
		'IUSR:(OI)(CI)(IO)(F)',
	])
