from __future__ import generators
import logging
import pprint
import psycopg2
import psycopg2.extras
import yaml
from datetime import datetime

import model

class IssueProvider (model.Provider):
    table_name = "issue"

    def create (self, record):
        msg = "Inserting issue record for '{0}'."
        logging.info(msg.format(record["title"].encode("utf8")))
        record["uuid"] = self.generate_uuid()
        record["timestamp_creation"] = datetime.now()

        with self.get_db_cursor() as cur:
            cur.execute("INSERT INTO issue (uuid, status, url, image_url, site, lang, title, article_type, body, body_html, description, description_html, timestamp_creation, timestamp_publish) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (record["uuid"], 1, record["url"], record["image_url"], record["site"], record["lang"], record["title"], 'Issues', record["body"], record["body_html"], record["description"], record["description_html"], record["timestamp_creation"], record["timestamp_publish"],))
            return Issue(record)
    def update (self, record, request):
        msg = "Updating issue record for '{0}'."
        logging.info(msg.format(record.title.encode("utf8")))

        with self.get_db_cursor() as cur:
            for k in request.form:
                setattr(record, k, request.form[k])

            record.status = int(request.form["status"])

            cur.execute("UPDATE issue SET (status, url, image_url, site, lang, title, body, body_html, description, description_html, timestamp_publish) = (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) WHERE uuid=%s", (record.status, record.url, record.image_url, record.site, record.lang, record.title, record.body, record.body_html, record.description, record.description_html, record.timestamp_publish, record.uuid,))
            return True

    def exists (self, uuid):
        """ Returns True if record with uuid exists """
        return self.read (uuid) is not None

    def exists_by_url (self, url):
        """ Returns True if record with issue_id exists """
        return self.read_by_url (url) is not None

    def get_all_languages (self):
        with self.get_db_cursor() as cur:
            cur.execute ("SELECT DISTINCT lang FROM issue", ())
            return map (lambda x: x['lang'], cur)

    def get_all_sites (self):
        with self.get_db_cursor() as cur:
            cur.execute ("SELECT DISTINCT site FROM issue", ())
            return map (lambda x: x['site'], cur)

    def make_model (self, props):
        return Issue (props)

    def get_all(self):
        with self.get_db_cursor() as cur:
            cur.execute("SELECT * FROM issue ORDER BY timestamp_publish DESC")
            res = cur.fetchall()
            returns = []
            for record in res:
                if record is not None:
                    returns.append(Issue(record))
            return returns

    def read (self, uuid):
        with self.get_db_cursor() as cur:
            cur.execute("SELECT * FROM issue WHERE uuid = (%s)", (uuid,))
            res = cur.fetchone()

            if res is not None:
                return Issue (res)
            else:
                return None

    def read_by_url (self, url):
        with self.get_db_cursor() as cur:
            cur.execute("SELECT * FROM issue WHERE url = (%s)", (url,))
            res = cur.fetchone()

            if res is not None:
                return Issue (res)
            else:
                return None


class Issue (model.Model):
    object_type = 'issue'
