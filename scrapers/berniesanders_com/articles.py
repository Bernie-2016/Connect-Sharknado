import logging
import requests

from BeautifulSoup import BeautifulSoup
from datetime import datetime
from dateutil import parser
from HTMLParser import HTMLParser

from models.article import ArticleProvider
from scrapers.scraper import Scraper
from models.push import PushProvider
from utils.markdown import convert_markdown

logging.basicConfig(format="%(asctime)s - %(levelname)s : %(message)s",
                    level=logging.INFO)

class ArticlesScraper(Scraper):

    def __init__(self):
        Scraper.__init__(self)
        self.url = "https://berniesanders.com/daily/"
        self.html = HTMLParser()
        self.article_provider = ArticleProvider()
        self.push_provider = PushProvider()

    def retrieve_article(self, url):
        for x in range(3):
            r = requests.get(url)
            if "https://berniesanders.com" not in r.url:
                return r.url, False, False
            if r.status_code == 200:
                soup = BeautifulSoup(r.text)
                soup = self.sanitize_soup(soup)
                image = soup.find('meta', {'property': 'og:image'})['content']
                content = soup.article
                paragraphs = [self.html.unescape(self.replace_with_newlines(p))
                              for p in content.findAll("p")]
                text = "\n\n".join(paragraphs)
                html = "".join([str(p) for p in content.findAll("p")])
                return text, html, image
        return False, False, False

    def go(self):
        soup = self.get(self.url)
        content = soup.find("section", {"id": "content"})
        for article in content.findAll("article"):

            rec = {
            	"article_id": article['id'],
                "image_url": "",
                "body": "",
                "timestamp_publish": self.choose_publish_date(article.time["datetime"]),
                "site": "berniesanders.com",
                "lang": "en",
                "article_type": "DemocracyDaily",
                "excerpt": self.html.unescape(
                    article.find(
                        "div", {"class": "excerpt"}).p.text),
                "title": self.html.unescape(article.h2.text),
                "article_category": self.html.unescape(article.h1.string.strip()),
                "url": article.h2.a["href"]
            }
            if article.img is not None:
                rec["image_url"] = article.img["src"]

            text, html, image = self.retrieve_article(rec["url"])
            if text and not html:
                rec["body"] = text
                rec["body_markdown"] = text
                rec['article_type'] = "ExternalLink"
            elif text and html:
                rec["body"] = text
                rec['body_markdown'] = convert_markdown (html)
                print rec['body_markdown']
                exit(0)
                try:
                    article["image_url"]
                except KeyError:
                    article["image_url"] = image


            msg = ""
            if self.article_provider.exists_by_article_id(rec["article_id"]):
                print "found"
            else:
                print "not found"
                msg = "Inserting '{0}', created {1}"
                result = self.article_provider.create(rec)
                self.push_provider.create_by_foreign_model(result)

            logging.info(msg.format(
                rec["title"].encode("utf8"),
                str(rec["timestamp_publish"])
            ))

if __name__ == "__main__":
    bernie = ArticlesScraper()
    bernie.go()
