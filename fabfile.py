"""
Routines for installing, staging, and serving the Adams Row Tracker on Ubuntu.

To install on a clean Ubuntu Trusty box, simply run
fab bootstrap
"""

from fabric.api import sudo, run, task, env
from fabric.contrib import files
from jaraco.fabric import apt
from jaraco.fabric import context
from jaraco.util.string import (
	local_format as lf,
	global_format as gf,
)

if not env.hosts:
	env.hosts = ['elektra']

install_root = '/opt/Adams Row Tracker'
proc_name = 'adams-row-tracker'
site_name = 'adamsrowcondo.org'

@task
def bootstrap():
	install_env()
	update()
	configure_nginx()

@task
def install_env():
	sudo('rm -Rf "{install_root}"'.format(**globals()))
	install_upstart_conf()

@task
def install_upstart_conf(install_root=install_root):
	sudo(lf('mkdir -p "{install_root}"'))
	conf = gf("ubuntu/{proc_name}.conf")
	files.upload_template(conf, "/etc/init",
		use_sudo=True, context=vars())

@task
def update(version=None):
	install_to(install_root, version, use_sudo=True)
	cmd = gf('restart {proc_name} || start {proc_name}')
	sudo(cmd)

def install_to(root, version=None, use_sudo=False):
	"""
	Install jaraco.site to a PEP-370 environment at root. If version is
	not None, install that version specifically. Otherwise, use the latest.
	"""
	action = sudo if use_sudo else run
	pkg_spec = 'adamsrow.tracker'
	if version:
		pkg_spec += '==' + version
	action(lf('mkdir -p "{root}/lib/python2.7/site-packages"'))
	with apt.package_context('python-dev'):
		with context.shell_env(PYTHONUSERBASE=root):
			cmd = [
				'python', '-m',
				'easy_install',
				'--user',
				'-U',
				'-f', 'http://dl.dropbox.com/u/54081/cheeseshop/index.html',
				pkg_spec,
			]
			action(' '.join(cmd))

@task
def remove_all():
	sudo(gf('stop {proc_name} || echo -n'))
	sudo(gf('rm /etc/init/{proc_name}.conf || echo -n'))
	sudo(gf('rm -Rf "{install_root}"'))

@task
def configure_nginx():
	sudo('aptitude install -y nginx')
	source = "ubuntu/nginx config"
	target = gf("/etc/nginx/sites-available/{site_name}")
	files.upload_template(filename=source, destination=target, use_sudo=True,
		context=globals())
	cmd = gf(
		'ln -sf '
		'../sites-available/{site_name} '
		'/etc/nginx/sites-enabled/'
	)
	sudo(cmd)
	sudo('service nginx restart')
