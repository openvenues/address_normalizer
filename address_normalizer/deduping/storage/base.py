from address_normalizer.utils.enum import *
from address_normalizer.text.encoding import *

class storage_types(Enum):
    NOP = EnumValue(0, 'NOP')
    LEVELDB = EnumValue(1, 'LEVELDB')
    ROCKSDB = EnumValue(2, 'ROCKSDB')
    ELASTICSEARCH = EnumValue(3, 'ELASTICSEARCH')

storage_registry = {}

class NearDupeStorageMeta(type):
    def __init__(cls, name, bases, dict_):
        if 'abstract' not in dict_:
            cls.abstract = False
            if not hasattr(cls, 'storage_type'):
                raise NotImplementedError('NearDupeStorage sublclasses need to define storage_type property')
            storage_registry[cls.storage_type] = cls

class NearDupeStorage(object):
    abstract = True
    def __init__(self, *args, **kw):
        raise NotImplementedError('Children must implement')

    def get(self, key, default=None):
        raise NotImplementedError('Children must implement')

    # These two methods are for 
    def search(self, keys, default=None):
        return self._multiget(keys)

    def index(self, kvs):
        return self._multiput(kvs)

    def put(self, key, value):
        raise NotImplementedError('Children must implement')

    def _multiget(self, keys):
        raise NotImplementedError('Children must implement')

    def multiget(self, keys):
        return self._multiget(keys)

    def _multiput(self, kvs):
        raise NotImplementedError('Children must implement')

    def multiput(self, kvs):
        return self._multiput(kvs)

    def add_bloom_filter(self, bloom_filter):
        self.bloom_filter = bloom_filter
        self.multiget = self.bloom_filter_multiget
        self.search = self.bloom_filter_search
        self.multiput = self.bloom_filter_multiput

    def bloom_filter_multiget(self, keys, default=None):
        ret = {k: None for k in keys if k not in self.bloom_filter}

        remaining = set(keys) - set(ret)

        ret.update(self._multiget(remaining))
        return ret

    def bloom_filter_search(self, keys, default=None):
        return self.bloom_filter_multiget(keys, default=default)

    def bloom_filter_multiput(self, kvs, default=None):
        self.bloom_filter.update(kvs.keys())
        self._multiput(kvs)

class NopStorage(NearDupeStorage):
    storage_type = storage_types.NOP

    def __init__(self):
        pass

    def get(self, key, default=None):
        return default

    def put(self, key, value):
        pass

    def _multiget(self, keys, default=None):
        return {k: default for k in keys}

    def _multiput(self, kvs):
        pass
