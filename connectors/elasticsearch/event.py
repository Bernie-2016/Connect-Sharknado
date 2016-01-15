import connectors.elasticsearch.base
import models.event

class EventProvider (connectors.elasticsearch.base.Provider):
    def __init__ (self):
        self.event_provider = models.event.EventProvider()

    def get_current_objects (self):
        return filter (lambda x: x.status == 1, self.event_provider.get())

    def get_doc_types (self, version):
        return map (lambda x: x.replace('.','_'), self.event_provider.get_all_sites())

    def get_indices (self, version):
        return map (lambda x: "_".join (["events", x, version]), self.event_provider.get_all_languages())

    def get_object (self, id_, doc_type, index):
        obj = self.event_provider.read (id_)

        if obj is not None and obj.status == 1:
            return obj
        else:
            return None

    def get_search_data (self, obj, version):
        index = "_".join (["events", obj.lang, version])
        doc_type = obj.site.replace ('.', '_')
        body = obj.__dict__.copy()
        body['uuid'] = str (body['uuid'])
        body['object_type'] = obj.object_type

        body['venue'] = {
            'name': body['venue_name'],
            'city': body['venue_city'],
            'state': body['venue_state'],
            'zip': body['venue_zip'],
            'location': {
               'lon': float (body['longitude']),
               'lat': float (body['latitude'])
            }
        }

        for i in range(1,4):
            src_key = "venue_address"+str(i)
            trg_key = "address"+str(i)

            if body[src_key] != '' and body[src_key] is not None:
                body['venue'][trg_key] = body[src_key]


        del_keys = ["latitude", "longitude", "venue_address1", "venue_address2", "venue_address3", "venue_name", "venue_city", "venue_state", "venue_zip"]

        for del_key in del_keys:
            del body[del_key]

        return connectors.elasticsearch.base.SearchData (body['uuid'], index, doc_type, body)

    def get_search_filters (self):
        return [('object_type', 'event')]
