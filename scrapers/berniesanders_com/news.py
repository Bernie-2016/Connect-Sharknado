import logging
import requests

from BeautifulSoup import BeautifulSoup
from datetime import datetime
from dateutil import parser
from HTMLParser import HTMLParser

from models.news import NewsProvider
from scrapers.scraper import Scraper
from models.push import PushProvider
from utils.markdown import convert_markdown

logging.basicConfig(format="%(asctime)s - %(levelname)s : %(message)s",
                    level=logging.INFO)

class NewsScraper(Scraper):

    def __init__(self, url):
        Scraper.__init__(self)
        self.url = url
        self.html = HTMLParser()
        self.news_provider = NewsProvider()
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
        try:
            lang = soup.html['lang']
        except KeyError as e:
            lang = 'en'
        content = soup.find("section", {"id": "content"})
        for article in content.findAll("article"):
            rec = {
                "news_id": article['id'],
                "body": "",
                "image_url": "",
                "timestamp_publish": self.choose_publish_date(article.time["datetime"]),
                "site": "berniesanders.com",
                "lang": lang,
                "title": self.html.unescape(article.h2.text),
                "news_category": self.html.unescape(article.h1.string.strip()),
                "url": article.h2.a["href"]
            }
            if article.img is not None:
                rec["image_url"] = article.img["src"]

            # Pull excerpt if available
            try:
                rec["excerpt"] = self.html.unescape(article.p.text)
            except AttributeError:
                rec["excerpt"] = ""

            # Determine Type
            if rec['news_category'].lower() in ["on the road", "news"]:
                rec['news_type'] = "News"
            elif rec['news_category'].lower() in ["press release", "comunicados de prensa"]:
                rec['news_type'] = "PressRelease"
            else:
                rec['news_type'] = "Unknown"

            text, html, image = self.retrieve_article(rec["url"])
            if text and not html:
                rec["body"], rec["body_markdown"] = text, text
                rec['news_type'] = "ExternalLink"
            elif text and html:
                rec["body"] = text
                rec['body_markdown'] = convert_markdown (html)
                try:
                    article["image_url"]
                except KeyError:
                    article["image_url"] = image


            msg = ""
            if self.news_provider.exists_by_news_id(rec["news_id"]):
                print "found"
            else:
                print "not found"
                msg = "Inserting '{0}', created {1}"
                result = self.news_provider.create(rec)
                self.push_provider.create_by_foreign_model(result)

            logging.info(msg.format(
                rec["title"].encode("utf8"),
                str(rec["timestamp_publish"])
            ))

if __name__ == "__main__":
    # English
    bernieEn = NewsScraper("https://berniesanders.com/news/")
    bernieEn.go()
    # Spanish
    bernieEs = NewsScraper("https://berniesanders.com/es/comunicados-de-prensa/")
    bernieEs.go()
