from __future__ import generators
import logging
import pprint
import psycopg2
import psycopg2.extras
import yaml
from datetime import datetime

import model

class EventProvider (model.Provider):
    table_name = "event"

    def create (self, record):
        msg = "Inserting event record for '{0}'."
        logging.info(msg.format(record["name"].encode("utf8")))
        record["uuid"] = self.generate_uuid()
        record["timestamp_creation"] = datetime.now()

        with self.get_db_cursor() as cur:
            cur.execute("INSERT INTO event (uuid, event_id, event_id_obfuscated, url, name, date, start_time, timezone, description, latitude, longitude, is_official, attendee_count, capacity, site, lang, event_type_name, venue_address1, venue_address2, venue_address3, venue_name, venue_city, venue_state, venue_zip, timestamp_creation) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (record["uuid"], record["event_id"], record["event_id_obfuscated"], record["url"], record["name"], record["date"], record["start_time"], record["timezone"], record["description"], record["latitude"], record["longitude"], record["is_official"], record["attendee_count"], record["capacity"], record["site"], record["lang"], record["event_type_name"], record["venue_address1"], record["venue_address2"], record["venue_address3"], record["venue_name"], record["venue_city"], record["venue_state"], record["venue_zip"], record["timestamp_creation"],))
            return Event(record)

    def update (self, record, request):
        msg = "Updating event record for '{0}'."
        logging.info(msg.format(record.name.encode("utf8")))

        with self.get_db_cursor() as cur:
            for k in request.form:
                setattr(record, k, request.form[k])

            cur.execute("UPDATE event SET (status, event_id, event_id_obfuscated, url, name, date, start_time, timezone, description, latitude, longitude, is_official, attendee_count, capacity, site, lang, event_type_name, venue_address1, venue_address2, venue_address3, venue_name, venue_city, venue_state, venue_zip) = (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) WHERE uuid=%s", (record.status, record.event_id, record.event_id_obfuscated, record.url, record.name, record.date, record.start_time, record.timezone, record.description, record.latitude, record.longitude, record.is_official, record.attendee_count, record.capacity, record.site, record.lang, record.event_type_name, record.venue_address1, record.venue_address2, record.venue_address3, record.venue_name, record.venue_city, record.venue_state, record.venue_zip, record.uuid,))
            return True

    def get_all(self):
        with self.get_db_cursor() as cur:
            cur.execute("SELECT * FROM " + self.table_name + " ORDER BY start_time DESC")
            res = cur.fetchall()
            returns = []
            for record in res:
                if record is not None:
                    returns.append(Event(record))
            return returns

    def get_all_languages (self):
        with self.get_db_cursor() as cur:
            cur.execute ("SELECT DISTINCT lang FROM event", ())
            return map (lambda x: x['lang'], cur)

    def get_all_sites (self):
        with self.get_db_cursor() as cur:
            cur.execute ("SELECT DISTINCT site FROM event", ())
            return map (lambda x: x['site'], cur)

    def exists (self, uuid):
        """ Returns True if record with uuid exists """
        return self.read (uuid) is not None

    def exists_by_event_id (self, event_id):
        """ Returns True if record with event_id exists """
        return self.read_by_event_id (event_id) is not None

    def make_model (self, props):
        return Event (props)

    def read (self, uuid):
        with self.get_db_cursor() as cur:
            cur.execute("SELECT * FROM event WHERE uuid = (%s)", (uuid,))
            res = cur.fetchone()

            if res is not None:
                return Event (res)
            else:
                return None

    def read_by_event_id (self, event_id):
        with self.get_db_cursor() as cur:
            cur.execute("SELECT * FROM event WHERE event_id = (%s)", (event_id,))
            res = cur.fetchone()

            if res is not None:
                return Event (res)
            else:
                return None


class Event (model.Model):
    object_type = 'event'
