import connectors.elasticsearch.base
import models.event

class EventProvider (connectors.elasticsearch.base.Provider):
    def __init__ (self):
        self.event_provider = models.event.EventProvider()

    def get_current_objects (self):
        return self.event_provider.get()

    def get_doc_types (self, version):
        return map (lambda x: x.replace('.','_'), self.event_provider.get_all_sites())

    def get_indices (self, version):
        return map (lambda x: "_".join (["events", x, version]), self.event_provider.get_all_languages())

    def get_object (self, id_, doc_type, index):
        return self.event_provider.read (id_)

    def get_search_data (self, obj, version):
        index = "_".join (["events", obj.lang, version])
        doc_type = obj.site.replace ('.', '_')
        body = obj.__dict__.copy()
        body['uuid'] = str (body['uuid'])
        body['object_type'] = obj.object_type
        return connectors.elasticsearch.base.SearchData (body['uuid'], index, doc_type, body)

    def get_search_filters (self):
        return [('object_type', 'event')]
