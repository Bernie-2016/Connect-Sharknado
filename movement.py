import time
import sys
import yaml
import base64
reload(sys)
sys.setdefaultencoding('utf8')

from flask import Flask, request, session, url_for, redirect, render_template, abort, g, flash
from flask_httpauth import HTTPBasicAuth

from datetime import datetime

from models.event import EventProvider
from models.issue import IssueProvider
from models.video import VideoProvider
from models.article import ArticleProvider
from models.news import NewsProvider
from models.push import PushProvider
from models.news import News
from models.push import Push
from connectors.parse.base import ParseWrapper

app = Flask(__name__)
app.config.from_object(__name__)
auth = HTTPBasicAuth()

#change parse push message to api
#fix logging

@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None

# Home
@app.route('/')
@auth.login_required
def greeting():
	return render_template('index.html')


# Push Notifications
@app.route('/push/create', methods=['GET', 'POST'])
@auth.login_required
def push_create():
	if request.method == 'POST':
		data = dict((key, request.form.getlist(key)[0]) for key in request.form.keys())
		push = push_provider.create(data)
		if hasattr(push, 'uuid'):
			return redirect('/push/' + str(push.uuid))
	else:
		return render_template('push.html', push=Push({'object_type': 'Custom', 'object_uuid': ''}), updated=False)

@app.route('/push/list')
@auth.login_required
def push_list():
	pushes = push_provider.get_all()
	return render_template('push_list.html', pushes=pushes)

@app.route('/push/<uuid:push_uuid>', methods=['GET', 'POST'])
@auth.login_required
def push_detail(push_uuid):
	push = push_provider.read(push_uuid)
	updated = False
	msg = False
	alert_type = ''
	if request.method == 'POST':
		try:
			send_push = request.form['_send_push']
		except AttributeError as e:
			send_push = 0

		if push_provider.update(push, request):
			updated = True
			if send_push == '1':
				''' Push the notification '''
				parse = ParseWrapper()
				object_uuid = ''
				if push.object_uuid:
					object_uuid = push.object_uuid

				try:
					action = {
						'news' : 'openNewsArticle',
						'article': 'openNewsArticle',
						'video': 'openVideo'
					}[push.object_type]

					if parse.push(request.form['title'], action, object_uuid):
						push = push_provider.read(push_uuid)
						push_provider.set_pushed(push)
						alert_type = 'alert-success'
						msg = 'The following alert has been pushed: ' + request.form['title']
					else:
						alert_type = 'alert-danger'
						msg = 'Push notification failed. Record still saved.'

				except AttributeError as e:
					alert_type = 'alert-danger'
					msg = 'Push saved but notification sending failed: ' + e
			else:
				alert_type = 'alert-warning'
				msg = 'Push saved but not sent'

	return render_template('push.html', push=push, updated=updated, msg=msg, alert_type=alert_type)

# News
@app.route('/news/create', methods=['GET', 'POST'])
@auth.login_required
def news_create():
	if request.method == 'POST':
		data = dict((key, request.form.getlist(key)[0]) for key in request.form.keys())
		data['timestamp_publish'] = datetime.now()
		data['lang'] = 'en'

		news = news_provider.create(data)
		if hasattr(news, 'uuid'):
			return redirect('/news/' + str(news.uuid))
	else:
		return render_template('news.html', news=News({'news_type': 'PressRelease', 'news_category': 'Press Release'}), updated=False)

@app.route('/news/list')
@auth.login_required
def news_list():
	newss = news_provider.get_all()
	return render_template('news_list.html', newss=newss)

@app.route('/news/<uuid:news_uuid>', methods=['GET', 'POST'])
@auth.login_required
def news_detail(news_uuid):
	news = news_provider.read(news_uuid)
	updated = False
	if request.method == 'POST' and news_provider.update(news, request):
		updated = True
	return render_template('news.html', news=news, updated=updated)


# Articles
@app.route('/article/list')
@auth.login_required
def article_list():
	articles = article_provider.get_all()
	return render_template('article_list.html', articles=articles)

@app.route('/article/<uuid:article_uuid>', methods=['GET', 'POST'])
@auth.login_required
def article_detail(article_uuid):
	article = article_provider.read(article_uuid)
	updated = False
	if request.method == 'POST' and article_provider.update(article, request):
		updated = True
	return render_template('article.html', article=article, updated=updated)


# Events
@app.route('/event/list')
@auth.login_required
def event_list():
	events = event_provider.get_all()
	return render_template('event_list.html', events=events)

@app.route('/event/<uuid:event_uuid>', methods=['GET', 'POST'])
@auth.login_required
def event_detail(event_uuid):
	event = event_provider.read(event_uuid)
	updated = False
	if request.method == 'POST' and event_provider.update(event, request):
		updated = True
	return render_template('event.html', event=event, updated=updated)


# Videos
@app.route('/video/list')
@auth.login_required
def video_list():
	videos = video_provider.get_all()
	return render_template('video_list.html', videos=videos)

@app.route('/video/<uuid:video_uuid>', methods=['GET', 'POST'])
@auth.login_required
def video_detail(video_uuid):
	video = video_provider.read(video_uuid)
	updated = False
	if request.method == 'POST' and video_provider.update(video, request):
		updated = True
	return render_template('video.html', video=video, updated=updated)


# Issues
@app.route('/issue/list')
@auth.login_required
def issue_list():
	issues = issue_provider.get_all()
	return render_template('issue_list.html', issues=issues)

@app.route('/issue/<uuid:issue_uuid>', methods=['GET', 'POST'])
@auth.login_required
def issue_detail(issue_uuid):
	issue = issue_provider.read(issue_uuid)
	updated = False
	if request.method == 'POST' and issue_provider.update(issue, request):
		updated = True
	return render_template('issue.html', issue=issue, updated=updated)


if __name__ == '__main__':
	try:
 		with open('/opt/bernie/config.yml', 'r') as f:
			conf = yaml.load(f)['flask']
	except IOError:
		msg = "Could not open config file: {0}"
		logging.info(msg.format(self.configfile))
		raise
	else:
		event_provider = EventProvider()
		issue_provider = IssueProvider()
		video_provider = VideoProvider()
		article_provider = ArticleProvider()
		news_provider = NewsProvider()
		push_provider = PushProvider()
		users = {
			conf['httpauth_username'] : conf['httpauth_password']
		}
		app.run(host=conf['host'], debug=conf['debug'])
		register(conf['parse_application_id'], conf['parse_rest_api_key'], conf['parse_master_key'])
		#Push.message("Good morning", channels=["Mike Testing"])