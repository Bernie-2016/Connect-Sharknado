from __future__ import generators
import logging
import pprint
import psycopg2
import psycopg2.extras
import yaml
from datetime import datetime

import model

class VideoProvider (model.Provider):
    table_name = "video"

    def create (self, record):
        msg = "Inserting video record for '{0}'."
        logging.info(msg.format(record["title"].encode("utf8")))
        record["uuid"] = self.generate_uuid()
        record["timestamp_creation"] = datetime.now()

        with self.get_db_cursor() as cur:
            cur.execute("INSERT INTO video (uuid, status, video_id, site, title, description, thumbnail_url, timestamp_creation, timestamp_publish, description_snippet) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (record["uuid"], 1, record["video_id"], record["site"], record["title"], record["description"], record["thumbnail_url"], record["timestamp_creation"], record["timestamp_publish"], record["snippet"],))
            return Video(record)

    def update (self, record, request):
        msg = "Updating video record for '{0}'."
        logging.info(msg.format(record.title.encode("utf8")))

        with self.get_db_cursor() as cur:
            for k in request.form:
                setattr(record, k, request.form[k])

            record.status = int(request.form["status"])
            cur.execute("UPDATE video SET (status, video_id, url, site, title, description, thumbnail_url, timestamp_publish, description_snippet) = (%s, %s, %s, %s, %s, %s, %s, %s, %s) WHERE uuid=%s", (record.status, record.video_id, record.url, record.site, record.title, record.description, record.thumbnail_url, record.timestamp_publish, record.description_snippet, record.uuid,))
            return True

    def get_all(self):
        with self.get_db_cursor() as cur:
            cur.execute("SELECT * FROM video ORDER BY timestamp_publish DESC")
            res = cur.fetchall()
            returns = []
            for record in res:
                if record is not None:
                    returns.append(Video(record))
            return returns

    def exists (self, uuid):
        """ Returns True if record with uuid exists """
        return self.read (uuid) is not None

    def exists_by_video_id (self, video_id):
        """ Returns True if record with video_id exists """
        return self.read_by_video_id (video_id) is not None

    def get_all_sites (self):
        with self.get_db_cursor() as cur:
            cur.execute ("SELECT DISTINCT site FROM video", ())
            sites = []

            for row in cur:
                sites.append (row['site'])

            return sites

    def make_model (self, props):
        return Video (props)

    def read (self, uuid):
        with self.get_db_cursor() as cur:
            cur.execute("SELECT * FROM video WHERE uuid = (%s)", (uuid,))
            res = cur.fetchone()

            if res is not None:
                return Video (res)
            else:
                return None

    def read_by_video_id (self, video_id):
        with self.get_db_cursor() as cur:
            cur.execute("SELECT * FROM video WHERE video_id = (%s)", (video_id,))
            res = cur.fetchone()

            if res is not None:
                return Video (res)
            else:
                return None


class Video (model.Model):
    object_type = 'video'
