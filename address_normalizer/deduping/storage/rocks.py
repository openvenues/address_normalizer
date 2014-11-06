import rocksdb

from address_normalizer.deduping.storage.base import *

class RocksDBNearDupeStorage(NearDupeStorage):
	storage_type = storage_types.ROCKSDB

	def __init__(self, db):
		self.db = db

	def get(self, key, default=None):
		try:
			return self.db.get(safe_encode(key))
		except KeyError:
			return default

	def put(self, key, value):
		key = safe_encode(key)
		value = safe_encode(value)

		self.db.put(key, value)

	def _multiget(self, keys, default=None):
		return self.db.multi_get(map(safe_encode, keys))

	def _multiput(self, kvs):
		batch = rocksdb.WriteBatch()
		it = kvs.iteritems() if hasattr(kvs, 'iteritems') else iter(kvs)
		for k, v in it:
			batch.put(safe_encode(k), safe_encode(v))
		self.db.write(batch)