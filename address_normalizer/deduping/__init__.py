from address_normalizer.deduping.storage import *
from address_normalizer.deduping.near_duplicates import *

def init_dbs(app):
    storage = storage_from_config(app.config)
    AddressNearDupe.configure(storage)