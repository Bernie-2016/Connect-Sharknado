import abc
import logging
import pprint
import yaml
from elasticsearch import Elasticsearch, TransportError
from time import time

class SearchData:
    def __init__ (self, id_, index, doc_type, body=None, parent=None):
        self.id_ = id_
        self.index = index
        self.doc_type = doc_type
        self.body = body
        self.parent = parent

    # Eventually I want to compare existing data with ES-indexed data
    # so we can update it if its changed. But for right now, don't care
    #def compare_eq (self, other):

    def get_index_properties (self):
        """ Returns data in format appropriate for ElasticSearch method calls """
        props = {}
        props['id'] = self.id_
        props['index'] = self.index
        props['doc_type'] = self.doc_type

        if self.body is not None:
            props['body'] = { 'body': self.body }

        if self.parent is not None:
            props['parent'] = self.parent

        return props



class Provider:
    """ Object providing search/indexing related functions for an object type """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_current_objects (self):
        """ Get all objects from the db """
        return

    @abc.abstractmethod
    def get_doc_types (self, version):
        """ Return a list of all document types this provider might use """
        return

    @abc.abstractmethod
    def get_indices (self, version):
        """ Return a list of all indices this provider might use """
        return

    @abc.abstractmethod
    def get_object (self, id_, index, doc_type):
        """ Return the object (if it exists) matching the criteria given
            (Hint: you probably only need id_)
        """
        return

    @abc.abstractmethod
    def get_search_data (self, obj, version):
        """ Convert the object given to an instance of SearchData """
        return

    def get_search_filters (self, index, doc_type):
        """ Return a list of (key, value) tuples to filter on

            Imagine we had articles and issues sharing the same index/doc_type;
            currently they are each separate providers so the way it is now they
            would each delete each-others objects every time the sync ran. But if
            we add an 'object_type' field to each object then they can filter
            based on the object_type they own.

            ArticleProvider might filter on this:
                [('object_type', 'article')]

            And IssueProvider might filter like this:
                [('object_type', 'issue')]
        """
        return []


class ElasticSearchWrapper:
    """ Simple wrapper class around ElasticSearch
        This just handles config loading as well as mapping SearchData object
        arguments correctly to different ES calls.
    """
    def __init__ (self, configfile=None):
        if configfile is None:
            self.configfile = '/opt/bernie/config.yml'
        else:
            self.configfile = configfile

        self.config = self.get_config()
        self.connection = None

    def delete (self, search_data):
     """ Deletes an object from ElasticSearch
         Returns True if it was found and deleted, or False
         if it didn't exist in the first place
     """
     conn = self.get_connection()
     props = search_data.get_index_properties()

     if props.has_key ('body'):
         del props['body']

     if props.has_key ('parent'):
         del props['parent']

     try:
         res = conn.delete (**props)
     except TransportError as e:
         if e[0] == 404:
             return False
         raise

     return res['found']

    def get_config(self):
        try:
            with open(self.configfile, 'r') as f:
                conf = yaml.load(f)
        except IOError:
            msg = 'Could not open config file: {0}'
            logging.info(msg.format(self.configfile))
            raise
        else:
            return conf

    def get_connection (self):
        if self.connection is None:
            self.connection = Elasticsearch(self.config['elasticsearch']['host'])

        return self.connection

    def get (self, search_data):
        """ Looks up an object in ElasticSearch
            Returns either a new SearchData object, or None
        """
        conn = self.get_connection()
        props = search_data.get_index_properties()

        if props.has_key ('body'):
            del props['body']

        if props.has_key ('parent'):
            del props['parent']

        try:
            res = conn.get (**props)
        except TransportError as e:
            # Don't care if index doesn't exist
            if e[0] == 404:
                return None
            raise

        if res['found']:
            if res.has_key ('parent'):
                parent = res['parent']
            else:
                parent = None

            return SearchData (res['_id'], res['_index'], res['_type'], res['_source']['body'], parent)
        else:
            return None

    def get_ids (self, index, doc_type, query_string=None):
        """ Get all ids matching the index, doc_type, and query """
        conn = self.get_connection()

        if query_string is None:
           query_string = '*:*'

        params = {'index': index, 'doc_type': doc_type, '_source': False, 'q': query_string, 'size': 999999999}
        result = conn.search (**params)

        for hit in result['hits']['hits']:
            yield SearchData (hit['_id'], hit['_index'], hit['_type'])

    def index (self, search_data):
        """ Adds the SearchData to ElasticSearch """
        conn = self.get_connection()
        props = search_data.get_index_properties()
        props["timestamp"] = int(time())
        return conn.index (**props)

