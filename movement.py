import time
import hashlib
import sys
reload(sys)
sys.setdefaultencoding('utf8')

from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash
from datetime import datetime

from models.event import EventProvider
from models.issue import IssueProvider
from models.video import VideoProvider
from models.article import ArticleProvider

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def greeting():
	return render_template('index.html')

@app.route('/issues/list')
def issues_list():
	issues = issue_provider.get_all()
	return render_template('issues_list.html', issues=issues)

@app.route('/issue/<uuid:issue_uuid>')
def issue_detail(issue_uuid):
	issue = issue_provider.read(issue_uuid)
	return render_template('issue.html', issue=issue)

if __name__ == '__main__':
	event_provider = EventProvider()
	issue_provider = IssueProvider()
	video_provider = VideoProvider()
	article_provider = ArticleProvider()
	app.run(host='10.0.1.140', debug=True)