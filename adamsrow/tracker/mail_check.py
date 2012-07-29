import sys
import importlib

def check_mail(tracker_home):
	# enable the trace util
	importlib.import_module('win32traceutil')
	gw = importlib.import_module('roundup.scripts.roundup_mailgw')

	print("Checking mail...")

	sys.argv[1:] = [
		tracker_home,
		"pops",
		"tracker@adamsrowcondo.org:33eanFqm@pop.gmail.com",
	]
	gw.run()

if __name__ == '__main__':
	check_mail(r"C:\Inetpub\Adams Row Tracker")
