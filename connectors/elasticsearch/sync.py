from connectors.elasticsearch import VERSION
from connectors.elasticsearch.base import ElasticSearchWrapper
import logging

class Sync:
    def __init__ (self, connection):
        """ `Connection` should be an instance of ElasticSearchWrapper """
        self.connection = connection

    def delete_extras (self, provider):
        """ Deletes objects from ElasticSearch which no longer exist in the database """
        doc_types = provider.get_doc_types (VERSION)
        indices = provider.get_indices (VERSION)
        search_filters = provider.get_search_filters()

        qs = []
        for pair in search_filters:
            qs.append (':'.join ([pair[0], pair[1]]))

        query_string = ' OR '.join (qs)

        for ix in indices:
            for dt in doc_types:
                self.delete_extras_for_index_doc_type (provider, ix, dt, query_string)

    def delete_extras_for_index_doc_type (self, provider, index, doc_type, query_string):
        """ Finds and removes all extra objects for the given index, doc_type, and query """
        conn = self.get_connection()

        for sd in conn.get_ids (index, doc_type, query_string):
            if provider.get_object (sd.id_, sd.index, sd.doc_type) is None:
                msg = "Deleting {0}"
                logging.info (msg.format (sd.id_))
                conn.delete (sd)
            else:
                msg = "Found {0} db, ignoring"
                logging.info (msg.format (sd.id_))

    def get_connection (self):
        return self.connection

    def run (self, providers):
        """ Syncs ElasticSearch with each of the given providers """
        for provider in providers:
            self.sync_provider (provider)
            self.delete_extras (provider)

    def sync_provider (self, provider):
        """ Syncs ElasticSearch with the particular provider """
        conn = self.get_connection()
        logging.info ("Syncing provider '{0}'".format(provider.__class__.__name__))
        for obj in provider.get_current_objects():
            search_data = provider.get_search_data (obj, VERSION)

            # Eventually we can actually handle updates efficiently but for
            # now lets just do it the easy way
            msg = "Indexing {0}"
            logging.info (msg.format (search_data.id_))
            conn.index (search_data)
