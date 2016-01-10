import logging
import requests
import json
import os

from datetime import datetime

logging.basicConfig(format="%(asctime)s - %(levelname)s : %(message)s",
                    level=logging.INFO)

if __name__ == "__main__":
    if __package__ is None:
        import sys
        from os import path
        sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
        from scraper import Scraper
    else:
        from ..scraper import Scraper


class Bernie2016VideosScraper(Scraper):

    def __init__(self):
        Scraper.__init__(self)
        api_key = self.config["youtube"]["api_key"]
        self.url = "https://www.googleapis.com/youtube/v3/search"
        self.params = {
          "order": "date",
          "maxResults": 10,
          "channelId": "UCH1dpzjCEiGAt8CXkryhkZg",
          "key": api_key,
          "type": "upload",
          "part": "snippet"
        }
        self.details = Bernie2016VideoDetailScraper()

    def translate(self, json):
      idJson = json["id"]
      snippetJson = json["snippet"]

      record = {
        "site": "youtube.com",
        "video_id": idJson["videoId"],
        "title": snippetJson["title"],
        "snippet": snippetJson["description"],
        "thumbnail_url": snippetJson["thumbnails"]["high"]["url"],
        "timestamp_publish": snippetJson["publishedAt"]
      }
      return record

    def go(self):
        r = self.get(self.url, params=self.params, result_format="json")
        for item in r["items"]:
          idJson = item["id"]
          
          record = self.translate(item)
          record["description"] = self.fetch_full_description(idJson["videoId"])

          if self.video_exists(idJson["videoId"]):
            print "found"
          else:
            print "not found"
            msg = "Inserting record for '{0}'."
            logging.info(msg.format(record["title"]))
            record["timestamp_creation"] = datetime.now()
            self.cur.execute("INSERT INTO video (id, video_id, site, title, description, thumbnail_url, timestamp_creation, timestamp_publish, description_snippet) VALUES(default, %s, %s, %s, %s, %s, %s, %s, %s)", (record["video_id"], record["site"], record["title"], record["description"], record["thumbnail_url"], record["timestamp_creation"], record["timestamp_publish"], record["snippet"],))
            self.db.commit()


    def video_exists(self, video_id):
        self.cur.execute("SELECT * FROM video WHERE video_id = (%s)", (video_id,))
        return self.cur.fetchone() is not None

    def fetch_full_description(self, video_id):
        self.details.params = {
          "key": self.config["youtube"]["api_key"],
          "part": "snippet,contentDetails",
          "id": video_id
        }
        r = self.details.get(self.details.url, params=self.details.params, result_format="json")
        return r["items"][0]["snippet"]["description"]



class Bernie2016VideoDetailScraper(Scraper):

    def __init__(self):
        Scraper.__init__(self)
        api_key = self.config["youtube"]["api_key"]
        self.url = "https://www.googleapis.com/youtube/v3/videos"

    def go(self):
        return null


if __name__ == "__main__":
    bernie = Bernie2016VideosScraper()
    bernie.go()
