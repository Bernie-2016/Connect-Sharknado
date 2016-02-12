import logging
import types

from BeautifulSoup import BeautifulSoup
from datetime import datetime
from dateutil import parser
from HTMLParser import HTMLParser

from models.issue import IssueProvider
from scrapers.scraper import Scraper
from models.push import PushProvider
from utils.markdown import convert_markdown

logging.basicConfig(format="%(asctime)s - %(levelname)s : %(message)s",
                    level=logging.INFO)


class IssuesScraper(Scraper):

    def __init__(self):
        Scraper.__init__(self)
        self.url = "https://berniesanders.com/issues/feed/"
        self.html = HTMLParser()
        self.issue_provider = IssueProvider()
        self.push_provider = PushProvider()

    def collect_urls(self):
        records = []
        items = self.get(self.url).findAll("item")
        for item in items:
            record = {
                "title": self.html.unescape(item.title.text),
                "timestamp_publish": parser.parse(item.pubdate.text),
                "site": "berniesanders.com",
                "lang": "en",
                "description_html": item.description.text,
                "description": self.html.unescape(
                    BeautifulSoup(item.description.text).p.text),
                "url": item.link.nextSibling
            }
            records.append(record)
        return records

    def retrieve(self, record):

        soup = self.get(record["url"])

        # retrieve image from <meta property="og:image" content="https://berniesanders.com/wp-content/uploads/2015/07/072615_Bernie_NewOrleans-4382.jpg"/>
        meta_image = soup.findAll(attrs={"property":"og:image"})
        record["image_url"] = meta_image[0]["content"].encode('utf8')

        # reset soup to content     
        soup = self.sanitize_soup(soup.find("section", {"id": "content"}))
        while soup.article.style is not None:
            soup.article.style.extract()
        record["body_html"] = str(soup.article)
        text = []
        for elem in soup.article.recursiveChildGenerator():
            if isinstance(elem, types.StringTypes):
                text.append(self.html.unescape(elem.strip()))
            elif elem.name == 'br':
                text.append("")
        record["body"] = "\n".join(text)
        record['body_markdown'] = convert_markdown (record['body_html'])

        return record

    def go(self):
        urls = self.collect_urls()
        if not urls:
            logging.critical("Could not retrieve issues.")
            sys.exit(1)
        for url in urls:
            record = self.retrieve(url)
            if self.issue_provider.exists_by_url(record["url"]):
                print "found"
            else:
                msg = "Inserting record for '{0}'."
                logging.info(msg.format(record["title"].encode("utf8")))
                record["timestamp_creation"] = datetime.now()
                result = self.issue_provider.create(record)
                self.push_provider.create_by_foreign_model(result)


if __name__ == "__main__":
    i = IssuesScraper()
    i.go()
