import csv

import roundup.date
import roundup.instance
import dateutil.parser

def make_date(date_str):
	"Use dateutil to parse the date to roundup format"
	roundup_date = dateutil.parser.parse(date_str).strftime('%Y-%m-%d')
	return roundup.date.Date(roundup_date, offset=-5)

def read_issues(filename='issues.csv'):
	with open(filename) as csv_file:
		return list(csv.DictReader(csv_file))

def do_import(issues, roundup_home):
	global tracker, db
	tracker = roundup.instance.open(roundup_home)
	db = tracker.open('admin')
	for issue in issues:
		import_issue(issue)
	db.close()

def import_issue(issue):
	#status = db.getclass('status').lookup(issue['Status'])
	id = db.issue.create(
		title=issue['Title'],
		status = issue['Status'],
	)
	db.commit()
	bug = db.issue.getnode(id)
	msg_id = db.msg.create(
		content=issue['Discussion'],
		author='admin',
		date=make_date(issue['Start Date']),
	)
	messages = bug.messages
	messages.append(msg_id)
	bug.messages = messages # force a setattr
	db.commit()
	if issue['Completion']:
		completion_date = make_date(issue['Completion'])
		msg_id = db.msg.create(
			content = "Completed",
			author='admin',
			date=completion_date,
		)
		resolved_id = db.status.filter(None,{'name': 'resolved'})[0]
		bug.status = resolved_id
		messages = bug.messages
		messages.append(msg_id)
		bug.messages = messages

		db.commit()

def main():
	do_import(read_issues(), "Adams Row Tracker")

if __name__ == '__main__': main()
