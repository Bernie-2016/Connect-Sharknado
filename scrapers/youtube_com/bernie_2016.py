import logging
import requests
import json
import os

from models.video import VideoProvider
from models.push import PushProvider
from scrapers.scraper import Scraper

from datetime import datetime

logging.basicConfig(format="%(asctime)s - %(levelname)s : %(message)s",
                    level=logging.INFO)

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
        self.video_provider = VideoProvider()
        self.push_provider = PushProvider()

    def translate(self, json):
      idJson = json["id"]
      snippetJson = json["snippet"]

      record = {
        "site": "youtube.com",
        "video_id": idJson["videoId"],
        "url": "https://www.youtube.com/watch?v="+idJson["videoId"],
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
          record["title"] = record["title"].replace(" | Bernie Sanders", "")

          if self.video_provider.exists_by_video_id(idJson["videoId"]):
            print "found"
          else:
            print "not found"
            msg = "Inserting record for '{0}'."
            logging.info(msg.format(record["title"].encode("utf8")))
            record["timestamp_creation"] = datetime.now()
            video = self.video_provider.create(record)

            # Add push record for possible notification pushing
            push_record = {
              "object_type": "video",
              "object_uuid": video.uuid,
              "title": video.title + " - new video posted by Bernie Sanders",
              "body": "See this new video now",
              "url": video.url
            }
            push = self.push_provider.create(push_record)

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
