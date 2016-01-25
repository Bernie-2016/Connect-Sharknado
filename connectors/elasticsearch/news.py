import connectors.elasticsearch.base
import models.news

class NewsProvider (connectors.elasticsearch.base.Provider):
    def __init__ (self):
        self.news_provider = models.news.NewsProvider()
        self.article_provider = models.article.ArticleProvider()

    def get_current_objects (self):
        return filter (lambda x: x.status == 1, self.news_provider.get())

    def get_doc_types (self, version):
        return map (lambda x: x.replace('.','_'), self.news_provider.get_all_sites())

    def get_indices (self, version):
        return map (lambda x: "_".join (["articles", x, version]), self.news_provider.get_all_languages())

    def get_object (self, id_, doc_type, index):
        obj = self.news_provider.read (id_)

        if obj is not None and obj.status == 1:
            return obj
        else:
            # test from article
            obj = self.article_provider.read (id_)

            if obj is not None and obj.status == 1:
                return obj
            else:
                return None

    def get_search_data (self, obj, version):
        index = "_".join (["articles", obj.lang, version])
        doc_type = obj.site.replace ('.', '_')
        body = obj.__dict__.copy()
        body['uuid'] = str (body['uuid'])
        body['article_type'] = body['news_type']
        body['object_type'] = obj.object_type
        return connectors.elasticsearch.base.SearchData (body['uuid'], index, doc_type, body)

    def get_search_filters (self):
        return [('object_type', 'article')]
