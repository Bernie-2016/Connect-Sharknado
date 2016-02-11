import logging
import requests

from BeautifulSoup import BeautifulSoup
from datetime import datetime
from dateutil import parser
from HTMLParser import HTMLParser

from models.news import NewsProvider
from scrapers.scraper import Scraper
from models.push import PushProvider

logging.basicConfig(format="%(asctime)s - %(levelname)s : %(message)s",
                    level=logging.INFO)

class NewsScraper(Scraper):

    def __init__(self):
        Scraper.__init__(self)
        self.url = "https://berniesanders.com/news/"
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
        content = soup.find("section", {"id": "content"})
        for article in content.findAll("article"):
            rec = {
                "news_id": article['id'],
                "image_url": "",
                "timestamp_publish": parser.parse(article.time["datetime"]),
                "site": "berniesanders.com",
                "lang": "en",
                "title": self.html.unescape(article.h2.text),
                "news_category": self.html.unescape(article.h1.string.strip()),
                "url": article.h2.a["href"]
            }
            if article.img is not None:
                rec["image_url"] = article.img["src"]

            # Pull excerpt if available
            try:
                rec["excerpt_html"] = str(article.p)
                rec["excerpt"] = self.html.unescape(article.p.text)
            except AttributeError:
                rec["excerpt"], rec["excerpt_html"] = "", ""

            # Determine Type
            if rec['news_category'].lower() in ["on the road", "news"]:
                rec['news_type'] = "News"
            elif rec['news_category'].lower() == "press release":
                rec['news_type'] = "PressRelease"
            else:
                rec['news_type'] = "Unknown"

            text, html, image = self.retrieve_article(rec["url"])
            if text and not html:
                rec["body"], rec["body_html"] = text, text
                rec['news_type'] = "ExternalLink"
                rec["body_html_nostyle"] = ""
            elif text and html:
                rec["body"], rec["body_html"] = text, html

                no_style = self.remove_style(BeautifulSoup(html))
                rec["body_html_nostyle"] = "".join([str(p) for p in no_style.findAll("p")])

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
    bernie = NewsScraper()
    bernie.go()
