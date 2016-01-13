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
            cur.execute("INSERT INTO article (uuid, article_id, site, title, description, thumbnail_url, timestamp_creation, timestamp_publish, description_snippet) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)", (record["uuid"], record["article_id"], record["site"], record["title"], record["description"], record["thumbnail_url"], record["timestamp_creation"], record["timestamp_publish"], record["snippet"],))
            return Article(record)

    def exists (self, uuid):
        """ Returns True if record with uuid exists """
        return self.read (uuid) is not None

    def exists_by_article_id (self, article_id):
        """ Returns True if record with article_id exists """
        return self.read_by_article_id (article_id) is not None

    def make_model (self, props):
        return Article (props)

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


class Article (model.Model):
    object_type = 'article'
