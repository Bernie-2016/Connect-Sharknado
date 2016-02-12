from __future__ import generators
import logging
import pprint
import psycopg2
import psycopg2.extras
import yaml
from datetime import datetime

import model

class ArticleProvider (model.Provider):
    table_name = "article"

    def create (self, record):
        msg = "Inserting article record for '{0}'."
        logging.info(msg.format(record["title"].encode("utf8")))
        record["uuid"] = self.generate_uuid()
        record["timestamp_creation"] = datetime.now()

        with self.get_db_cursor() as cur:
            cur.execute("INSERT INTO article (uuid, status, article_id, timestamp_creation, timestamp_publish, title, article_type, site, lang, excerpt_html, excerpt, article_category, url, image_url, body, body_html, body_html_nostyle, body_markdown) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (record["uuid"], 1, record["article_id"], record["timestamp_creation"], record["timestamp_publish"], record["title"], record["article_type"], record["site"], record["lang"], record["excerpt_html"], record["excerpt"], record["article_category"], record["url"], record["image_url"], record["body"], record["body_html"], record["body_html_nostyle"], record['body_markdown']))
            return Article(record)
            
    def update (self, record, request):
        msg = "Updating article record for '{0}'."
        logging.info(msg.format(record.title.encode("utf8")))

        with self.get_db_cursor() as cur:
            for k in request.form:
                setattr(record, k, request.form[k])

            record.status = int(request.form["status"])

            cur.execute("UPDATE article SET (status, article_id, timestamp_publish, title, article_type, site, lang, excerpt_html, excerpt, article_category, url, image_url, body, body_html, body_html_nostyle, body_markdown) = (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) WHERE uuid=%s", (record.status, record.article_id, record.timestamp_publish, record.title, record.article_type, record.site, record.lang, record.excerpt_html, record.excerpt, record.article_category, record.url, record.image_url, record.body, record.body_html, record.body_html_nostyle, record.body_markdown, record.uuid,))
            return True

    def exists (self, uuid):
        """ Returns True if record with uuid exists """
        return self.read (uuid) is not None

    def exists_by_article_id (self, article_id):
        """ Returns True if record with article_id exists """
        return self.read_by_article_id (article_id) is not None

    def exists_by_title_article_type (self, title, article_type):
        """ Returns True if record with title and article_type exists """
        return self.read_by_title_article_type (title, article_type) is not None

    def make_model (self, props):
        return Article (props)

    def get_all(self):
        with self.get_db_cursor() as cur:
            cur.execute("SELECT * FROM article ORDER BY timestamp_publish DESC")
            res = cur.fetchall()
            returns = []
            for record in res:
                if record is not None:
                    returns.append(Article(record))
            return returns

    def get_all_languages (self):
        with self.get_db_cursor() as cur:
            cur.execute ("SELECT DISTINCT lang FROM article", ())
            return map (lambda x: x['lang'], cur)

    def get_all_sites (self):
        with self.get_db_cursor() as cur:
            cur.execute ("SELECT DISTINCT site FROM article", ())
            return map (lambda x: x['site'], cur)

    def read (self, uuid):
        with self.get_db_cursor() as cur:
            cur.execute("SELECT * FROM article WHERE uuid = (%s)", (uuid,))
            res = cur.fetchone()

            if res is not None:
                return Article (res)
            else:
                return None

    def read_by_article_id (self, article_id):
       with self.get_db_cursor() as cur:
           cur.execute("SELECT * FROM article WHERE article_id = (%s)", (article_id,))
           res = cur.fetchone()
    
           if res is not None:
               return Article (res)
           else:
               return None

    def read_by_title_article_type (self, title, article_type):
        with self.get_db_cursor() as cur:
            cur.execute("SELECT * FROM article WHERE title = (%s) AND article_type = (%s)", (title, article_type))
            res = cur.fetchone()

            if res is not None:
                return Article (res)
            else:
                return None

class Article (model.Model):
    object_type = 'article'
