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

@app.route('/event/list')
def event_list():
	events = event_provider.get_all()
	return render_template('event_list.html', events=events)

@app.route('/event/<uuid:event_uuid>', methods=['GET', 'POST'])
def event_detail(event_uuid):
	event = event_provider.read(event_uuid)
	updated = False
	if request.method == 'POST' and event_provider.update(event, request):
		updated = True
	return render_template('event.html', event=event, updated=updated)

@app.route('/video/list')
def video_list():
	videos = video_provider.get_all()
	return render_template('video_list.html', videos=videos)

@app.route('/video/<uuid:video_uuid>', methods=['GET', 'POST'])
def video_detail(video_uuid):
	video = video_provider.read(video_uuid)
	updated = False
	if request.method == 'POST' and video_provider.update(video, request):
		updated = True
	return render_template('video.html', video=video, updated=updated)

@app.route('/issue/list')
def issue_list():
	issues = issue_provider.get_all()
	return render_template('issue_list.html', issues=issues)

@app.route('/issue/<uuid:issue_uuid>', methods=['GET', 'POST'])
def issue_detail(issue_uuid):
	issue = issue_provider.read(issue_uuid)
	updated = False
	if request.method == 'POST' and issue_provider.update(issue, request):
		updated = True
	return render_template('issue.html', issue=issue, updated=updated)

if __name__ == '__main__':
	event_provider = EventProvider()
	issue_provider = IssueProvider()
	video_provider = VideoProvider()
	article_provider = ArticleProvider()
	app.run(host='10.0.1.140', debug=True)