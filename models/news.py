from __future__ import generators
import logging
import pprint
import psycopg2
import psycopg2.extras
import yaml
from datetime import datetime

import model

class NewsProvider (model.Provider):
    table_name = "news"

    def create (self, record):
        msg = "Inserting news record for '{0}'."
        logging.info(msg.format(record["title"].encode("utf8")))
        record["uuid"] = self.generate_uuid()
        record["timestamp_creation"] = datetime.now()

        with self.get_db_cursor() as cur:
            cur.execute("INSERT INTO news (uuid, status, news_id, timestamp_creation, timestamp_publish, title, news_type, site, lang, excerpt_html, excerpt, news_category, url, image_url, body, body_html, body_html_nostyle) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (record["uuid"], 1, record["news_id"], record["timestamp_creation"], record["timestamp_publish"], record["title"], record["news_type"], record["site"], record["lang"], record["excerpt_html"], record["excerpt"], record["news_category"], record["url"], record["image_url"], record["body"], record["body_html"], record["body_html_nostyle"]))
            return News(record)

    def update (self, record, request):
        msg = "Updating news record for '{0}'."
        logging.info(msg.format(record.title.encode("utf8")))

        with self.get_db_cursor() as cur:
            for k in request.form:
                setattr(record, k, request.form[k])

            record.status = int(request.form["status"])
            cur.execute("UPDATE news SET (status, news_id, timestamp_publish, title, news_type, site, lang, excerpt_html, excerpt, news_category, url, image_url, body, body_html, body_html_nostyle) = (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) WHERE uuid=%s", (record.status, record.news_id, record.timestamp_publish, record.title, record.news_type, record.site, record.lang, record.excerpt_html, record.excerpt, record.news_category, record.url, record.image_url, record.body, record.body_html, record.body_html_nostyle, record.uuid,))
            return True

    def exists (self, uuid):
        """ Returns True if record with uuid exists """
        return self.read (uuid) is not None

    def exists_by_news_id (self, news_id):
        """ Returns True if record with news_id exists """
        return self.read_by_news_id (news_id) is not None

    def exists_by_title_news_type (self, title, news_type):
        """ Returns True if record with title and news_type exists """
        return self.read_by_title_news_type (title, news_type) is not None

    def make_model (self, props):
        return News (props)

    def get_all(self):
        with self.get_db_cursor() as cur:
            cur.execute("SELECT * FROM news ORDER BY timestamp_publish DESC")
            res = cur.fetchall()
            returns = []
            for record in res:
                if record is not None:
                    returns.append(News(record))
            return returns

    def get_all_languages (self):
        with self.get_db_cursor() as cur:
            cur.execute ("SELECT DISTINCT lang FROM news", ())
            return map (lambda x: x['lang'], cur)

    def get_all_sites (self):
        with self.get_db_cursor() as cur:
            cur.execute ("SELECT DISTINCT site FROM news", ())
            return map (lambda x: x['site'], cur)

    def read (self, uuid):
        with self.get_db_cursor() as cur:
            cur.execute("SELECT * FROM news WHERE uuid = (%s)", (uuid,))
            res = cur.fetchone()

            if res is not None:
                return News (res)
            else:
                return None

    def read_by_news_id (self, news_id):
       with self.get_db_cursor() as cur:
           cur.execute("SELECT * FROM news WHERE news_id = (%s)", (news_id,))
           res = cur.fetchone()
    
           if res is not None:
               return News (res)
           else:
               return None

    def read_by_title_news_type (self, title, news_type):
        with self.get_db_cursor() as cur:
            cur.execute("SELECT * FROM news WHERE title = (%s) AND news_type = (%s)", (title, news_type))
            res = cur.fetchone()

            if res is not None:
                return News (res)
            else:
                return None

class News (model.Model):
    object_type = 'news'
