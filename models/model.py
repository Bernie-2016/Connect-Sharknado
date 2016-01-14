import logging
import pprint
import psycopg2
import psycopg2.extras
import yaml
import abc
import uuid
from datetime import datetime


psycopg2.extras.register_uuid()

class Provider:
    __metaclass__ = abc.ABCMeta

    def __init__(self, configfile=None):
        if configfile is None:
            self.configfile = "/opt/bernie/config.yml"
        else:
            self.configfile = configfile

        self.config = self.get_config()
        self.db = None

    def connect (self):
        c = self.config["postgresql"]
        db = psycopg2.connect("host=" + c["host"] + " dbname=" + c["dbname"] + " user=" + c["dbuser"] + " password=" + c["dbpass"])
        db.autocommit = True
        return db

    def generate_uuid(self):
        return uuid.uuid4()

    def get_config(self):
        try:
            with open(self.configfile, 'r') as f:
                conf = yaml.load(f)
        except IOError:
            msg = "Could not open config file: {0}"
            logging.info(msg.format(self.configfile))
            raise
        else:
            return conf

    def get_db (self):
        if self.db is None:
            self.db = self.connect()
            # Time Zone only needs to be set once per connection
            cur = self.db.cursor()
            cur.execute ("SET TIME ZONE 'UTC'")
            cur.close()
        return self.db

    def get_db_cursor (self):
        """
        From the psycopg docs:
        But note that cursors used to fetch result sets will cache the data and
        use memory in proportion to the result set size. Our suggestion is to
        almost always create a new cursor and dispose old ones as soon as the
        data is not required anymore (call close() on them.) The only exception
        are tight loops where one usually use the same cursor for a whole bunch
        of INSERTs or UPDATEs.
        """
        db = self.get_db()
        # RealDictCursor so we can access our results by column-name
        return db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

    def get (self, size = 100):
        """
        Yields all objects from the current table.
        The 'size' parameter controls how many rows are fetched from
        the server at a time.
        """
        with self.get_db_cursor() as cur:
            query = cur.mogrify("SELECT * FROM %s" % (self.table_name))
            cur.execute (query)
            res = cur.fetchmany(size)

            while len(res) > 0:
                for r in res:
                    yield self.make_model (r)
                res = cur.fetchmany(size)

    @abc.abstractmethod
    def make_model (self, props):
        """
        Take a dictionary of properties and converts it to the relevant
        Model object
        """
        return

class Model:
    def __init__(self, props):
        for k,v in props.iteritems():
            # Ugh, `id` is a builtin python function and its use as a variable
            # or property name is frowned upon. The recommended convention is
            # to use `id_` instead
            if k == 'id':
                self.id_ = v
            else:
                setattr (self, k, v)
