import connectors.elasticsearch.base
import models.video

class VideoProvider (connectors.elasticsearch.base.Provider):
    def __init__ (self):
        self.video_provider = models.video.VideoProvider()

    def get_current_objects (self):
        return filter (lambda x: x.status == 1, self.video_provider.get())

    def get_doc_types (self, version):
        return map (lambda x: x.replace('.','_'), self.video_provider.get_all_sites())

    def get_indices (self, version):
        return ["_".join (["videos", version])]

    def get_object (self, id_, doc_type, index):
        obj = self.video_provider.read (id_)

        if obj is not None and obj.status == 1:
            return obj
        else:
            return None

    def get_search_data (self, obj, version):
        index = "_".join (["videos", version])
        doc_type = obj.site.replace ('.', '_')
        body = obj.__dict__.copy()
        body['uuid'] = str (body['uuid'])
        body['object_type'] = obj.object_type
        return connectors.elasticsearch.base.SearchData (body['uuid'], index, doc_type, body)

    def get_search_filters (self):
        return [('object_type', 'video')]
