from address_normalizer.deduping.storage.base import *

from leveldb import LevelDB, WriteBatch

class LevelDBNearDupeStorage(NearDupeStorage):
	storage_type = storage_types.LEVELDB

	def __init__(self, db):
		self.db = db

	def get(self, key, default=None):
		try:
			return self.db.Get(safe_encode(key))
		except KeyError:
			return default

	def put(self, key, value):
		key = safe_encode(key)
		value = safe_encode(value)

		self.db.Put(key, value)

	def _multiget(self, keys, default=None):
		return {k: self.get(k, default) for k in keys}

	def _multiput(self, kvs):
		batch = WriteBatch()
		it = kvs.iteritems() if hasattr(kvs, 'iteritems') else iter(kvs)
		for k, v in it:
			batch.Put(safe_encode(k),safe_encode(v))
		self.db.Write(batch, sync=True)