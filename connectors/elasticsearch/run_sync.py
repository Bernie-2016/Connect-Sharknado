import logging

from connectors.elasticsearch.base import ElasticSearchWrapper
from connectors.elasticsearch.sync import Sync
from connectors.elasticsearch.article import ArticleProvider
from connectors.elasticsearch.event import EventProvider
from connectors.elasticsearch.issue import IssueProvider
from connectors.elasticsearch.video import VideoProvider
from connectors.elasticsearch.news import NewsProvider

def main (args=None):

    logging.basicConfig(format="%(asctime)s - %(levelname)s : %(message)s", level=logging.INFO)
    sync = Sync (ElasticSearchWrapper())

    providers = []
    providers.append (ArticleProvider())
    providers.append (EventProvider())
    providers.append (IssueProvider())
    providers.append (VideoProvider())
    providers.append (NewsProvider())

    sync.run (providers)




main()
