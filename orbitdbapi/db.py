import json
import logging
from copy import deepcopy
from collections.abc import Hashable, Iterable
from urllib.parse import quote as urlquote


class DB ():
    def __init__(self, client, params, **kwargs):
        self.__cache = {}
        self.__client = client
        self.__params = params
        self.__dbname = params['dbname']
        self.__id = params['id']
        self.__id_safe = urlquote(self.__id, safe='')
        self.__type = params['type']
        self.__use_cache = kwargs.get('use_db_cache')
        self.logger = logging.getLogger(__name__)

        if hasattr( self.params, 'indexBy'):
            self.index_by = self.__params.indexBy

    def clear_cache(self):
        self.__cache = {}

    def cache_get(self, item):
        item = str(item)
        return deepcopy(self.__cache.get(item))

    def cache_remove(self, item):
        item = str(item)
        if item in self.__cache:
            del self.__cache[item]

    @property
    def cache(self):
        return deepcopy(self.__cache)

    @property
    def params(self):
        return deepcopy(self.__params)

    @property
    def dbname(self):
        return self.__dbname

    @property
    def dbtype(self):
        return self.__type

    @property
    def queryable(self):
        return 'query' in self.__params.get('capabilities', {})
    @property
    def putable(self):
        return 'put' in self.__params.get('capabilities', {})

    def info(self):
        endpoint = '/'.join(['db', self.__id_safe])
        return self.__client._call('get', endpoint)

    def get(self, item, cache=None):
        if cache is None: cache = self.__use_cache
        item = str(item)
        if cache and item in self.__cache:
            result = deepcopy(self.__cache[item])
        else:
            endpoint = '/'.join(['db', self.__id_safe, item])
            result = self.__client._call('get', endpoint)
            if cache: self.__cache[item] = result
        if isinstance(result, Hashable): return deepcopy(result)
        #if isinstance(result, Iterable): return deepcopy(next(result, {}))
        #if isinstance(result, list): return deepcopy(next(iter(result), {}))
        return result

    def get_raw(self, item):
        endpoint = '/'.join(['db', self.__id_safe, 'raw', str(item)])
        return (self.__client._call('get', endpoint))

    def put(self,  item, cache=None):
        if cache is None: cache = self.__use_cache
        if cache:
            if hasattr(self, 'index_by'):
                if hasattr(item, self.index_by):
                    index_val = getattr(item, self.index_by)
                else:
                    index_val = item[self.index_by]
                self.__cache[index_val] = item
        endpoint = '/'.join(['db', self.__id_safe, 'put'])
        entry_hash = self.__client._call('post', endpoint, item)
        if cache: self.__cache[entry_hash] = item
        return entry_hash

    def add(self, item, cache=None):
        if cache is None: cache = self.__use_cache
        endpoint = '/'.join(['db', self.__id_safe, 'add'])
        entry_hash = self.__client._call('post', endpoint, item)
        if cache: self.__cache[entry_hash] = item
        return entry_hash

    def iterator_raw(self, params):
        endpoint =  '/'.join(['db', self.__id_safe, 'rawiterator'])
        return self.__client._call('get', endpoint, params)

    def iterator(self, params):
        endpoint =  '/'.join(['db', self.__id_safe, 'iterator'])
        return self.__client._call('get', endpoint, params)

    def index(self):
        endpoint = '/'.join(['db', self.__id_safe, 'index'])
        result = self.__client._call('get', endpoint)
        self.__cache = result
        return result

    def unload(self):
        endpoint = '/'.join(['db', self.__id_safe])
        return self.__client._call('delete', endpoint)