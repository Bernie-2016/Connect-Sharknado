from __future__ import generators
import logging
import pprint
import psycopg2
import psycopg2.extras
import yaml
from datetime import datetime

import model

class PushProvider (model.Provider):
    table_name = "push"

    def create (self, record):
        if self.exists_by_url(record["url"]):
            msg = "Found url {0}."
            logging.info(msg.format(record["url"].encode("utf8")))
            return False

        msg = "Inserting push record for '{0}'."
        logging.info(msg.format(record["title"].encode("utf8")))
        record["uuid"] = self.generate_uuid()
        record["timestamp_creation"] = datetime.now()
        record["timestamp_publish"] = datetime.now()

        if self.validate_uuid4(record["object_uuid"]) is False:
            record["object_uuid"] = self.generate_uuid()

        with self.get_db_cursor() as cur:
            cur.execute("INSERT INTO push (uuid, status, object_type, object_uuid, title, body, url, timestamp_creation, timestamp_publish) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)", (record["uuid"], 1, record["object_type"], record["object_uuid"], record["title"], record["body"], record["url"], record["timestamp_creation"], record["timestamp_publish"],))
            return Push(record)

    def update (self, record, request):
        msg = "Updating push record for '{0}'."
        logging.info(msg.format(record.title.encode("utf8")))

        with self.get_db_cursor() as cur:
            for k in request.form:
                setattr(record, k, request.form[k])

            record.status = int(request.form["status"])
            cur.execute("UPDATE push SET (status, object_type, object_uuid, title, body, url, timestamp_publish) = (%s, %s, %s, %s, %s, %s, %s) WHERE uuid=%s", (record.status, record.object_type, record.object_uuid, record.title, record.body, record.url, record.timestamp_publish, record.uuid,))

            return True

    def set_pushed (self, record):
        msg = "Setting pushed status for push record '{0}'."
        logging.info(msg.format(record.title.encode("utf8")))
        with self.get_db_cursor() as cur:
            record.timestamp_publish = datetime.now()
            record.status = 2
            cur.execute("UPDATE push SET (status, object_type, object_uuid, title, body, url, timestamp_publish) = (%s, %s, %s, %s, %s, %s, %s) WHERE uuid=%s", (record.status, record.object_type, record.object_uuid, record.title, record.body, record.url, record.timestamp_publish, record.uuid,))

            return True


    def exists (self, uuid):
        """ Returns True if record with uuid exists """
        return self.read (uuid) is not None

    def exists_by_url (self, url):
        """ Returns True if record with url exists """
        return self.read_by_url (url) is not None

    def make_model (self, props):
        return Push (props)

    def get_object_title(self, push):
        with self.get_db_cursor() as cur:
            if push.object_type == 'video':
                cur.execute("SELECT title FROM video WHERE uuid = (%s)", (push.object_uuid,))
                res = cur.fetchone()

                if res is not None:
                    return res.title;
                else:
                    return None;

    def get_all(self):
        with self.get_db_cursor() as cur:
            cur.execute("SELECT * FROM push ORDER BY timestamp_creation DESC")
            res = cur.fetchall()
            returns = []
            for record in res:
                if record is not None:
                    returns.append(Push(record))
            return returns

    def read (self, uuid):
        with self.get_db_cursor() as cur:
            cur.execute("SELECT * FROM push WHERE uuid = (%s)", (uuid,))
            res = cur.fetchone()

            if res is not None:
                return Push (res)
            else:
                return None

    def read_by_object_uuid (self, url):
        with self.get_db_cursor() as cur:
            cur.execute("SELECT * FROM push WHERE object_uuid = (%s)", (object_uuid,))
            res = cur.fetchone()

            if res is not None:
                return Push (res)
            else:
                return None

    def read_by_url (self, url):
        with self.get_db_cursor() as cur:
            cur.execute("SELECT * FROM push WHERE url = (%s)", (url,))
            res = cur.fetchone()

            if res is not None:
                return Push (res)
            else:
                return None

    def create_by_foreign_model (self, model):
        ''' Create a push record from a foreign model object '''
        try:
            push = {
                "object_type": model.object_type,
                "object_uuid": model.uuid,
                "body": '',
                "url": model.url
            }
        except AttributeError as e:
            msg = "Push could not be created because missing attribute: {0}."
            logging.info(msg.format(e.encode("utf8")))
            return False

        if hasattr(model, 'body'):
            push["body"] = model.body

        if hasattr(model, 'title'):
            push["title"] = model.title
        elif hasattr(model, 'name'):
            push["title"] = model.name
        else:
            push["title"] = ''

        return self.create(push)

class Push (model.Model):
    object_type = 'push'