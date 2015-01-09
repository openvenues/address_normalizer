import geohash
import logging

import operator

from functools import partial

from itertools import chain, product, combinations, imap

from address_normalizer.deduping.duplicates import *
from address_normalizer.deduping.storage.base import *

from address_normalizer.text.gazetteers import *
from address_normalizer.text.normalize import *

from address_normalizer.models.address import *
from address_normalizer.models.venue import *

near_dupe_registry = {}

# Two lat/longs sharing a geohash prefix of 6 characters are within about 610 meters of each other
DEFAULT_GEOHASH_PRECISION = 6

logger = logging.getLogger('near_dupes')

class NearDupeMeta(type):
    def __init__(cls, name, bases, dict_):
        if 'abstract' not in dict_:
            near_dupe_registry[cls.__entity_type__] = cls
            
        super(NearDupeMeta, cls).__init__(name, bases, dict_)

    dupe_cache = {}


class NearDupe(object):
    abstract = True
    __metaclass__ = NearDupeMeta
    
    key_generators = ()
    
    configured = False
    storage = NopStorage()

    @classmethod
    def configure(cls, storage):
        cls.storage = storage

    @classmethod
    def find_dupes(cls, ents):
        if not ents:
            return {}, {}, {}
        
        entity_dict = {e.guid: e for e in ents}
        clusters = defaultdict(set)
        _ = [clusters[safe_encode(c)].add(ent.guid) for ent in ents for c in cls.gen_keys(ent)]
        clusters = dict(clusters)
        logger.info('{} clusters found'.format(len(clusters)))
        
        logger.info('Checking for local dupes')

        local_guid_pairs = set()
        local_dupes = {}

        for cluster_id, guids in clusters.iteritems():
            if len(guids) < 2:
                continue

            local_guid_pairs.update(combinations(guids, 2))

        for g1, g2 in local_guid_pairs:
            ent1 = entity_dict[g1]
            ent2 = entity_dict[g2]
            if cls.exact_dupe.is_dupe(ent1, ent2):
                cls.assign_local_dupe(local_dupes, ent1, ent2)
        
        logger.info('Checking global dupes')

        existing_clusters = defaultdict(list)

        if clusters:
            _ = [existing_clusters[c].append(guid) for c, guid in cls.storage.search(clusters.keys()).iteritems() if guid]

        existing_guids = set()
        existing_ents = {}
        
        if existing_clusters:
            existing_guids = set.union(*(set(v) for v in existing_clusters.itervalues()))
            existing_ents = {guid: cls.model(json.loads(e)) for guid, e in cls.storage.multiget(list(existing_guids)).iteritems() if e}
           
        global_dupes = {}

        global_guid_pairs = set([(new_guid, existing_guid) for cluster_id, existing in existing_clusters.iteritems() for new_guid, existing_guid in product(clusters[cluster_id], existing)])
        
        for new_guid, existing_guid in global_guid_pairs:
            local_ent = entity_dict[new_guid]
            existing_ent = existing_ents[existing_guid]
            if cls.exact_dupe.is_dupe(existing_ent, local_ent):
                cls.assign_global_dupe(global_dupes, existing_ent, local_ent)

        logger.info('Done with global dupe checking')    
        return clusters, local_dupes, global_dupes

    @classmethod
    def check(cls, objects, add=True):
        object_dict = {o.guid: o for o in objects}
        clusters, local_dupes, global_dupes = cls.find_dupes(objects)

        new_clusters = {}
        new_objects = {}

        dupes = local_dupes.copy()
        dupes.update(global_dupes)

        if add:
            for k, guids in clusters.iteritems():
                non_dupes = [g for g in guids if g not in dupes]
                if non_dupes:
                    guid = non_dupes[0]
                    new_clusters[k] = guid
                    new_objects[guid] = object_dict[guid]

            cls.add({guid: json.dumps(obj.to_primitive()) for guid, obj in  new_objects.iteritems()})
            cls.add_clusters(new_clusters)

        return [(obj, (dupes.get(obj.guid, obj.guid), obj.guid in dupes)) for obj in objects]

    @classmethod
    def assign_local_dupe(cls, dupes, existing, new):
        guid1 = existing.guid
        guid2 = new.guid

        guid1_existing = dupes.get(guid1)
        guid2_existing = dupes.get(guid2)

        if not guid1_existing and not guid2_existing:
            dupes[guid1] = guid2
        elif guid1_existing:
            dupes[guid2] = guid1_existing
        elif guid2_existing:
            dupes[guid1] = guid2_existing

    @classmethod
    def assign_global_dupe(cls, dupes, existing, new):
        dupes[new.guid] = existing.guid

    @classmethod
    def add(cls, kvs):
        cls.storage.multiput(kvs)

    @classmethod
    def add_clusters(cls, kvs):
        cls.storage.multiput(kvs)

class AddressNearDupe(NearDupe):
    __entity_type__ = Address.entity_type
    model = Address

    exact_dupe = AddressDupe
    geohash_precision = DEFAULT_GEOHASH_PRECISION

    street_gazetteers = list(chain(*[gazette_field_registry[f] for f in (address_fields.NAME, address_fields.HOUSE_NUMBER, address_fields.STREET)]))
    all_gazetteers = list(chain(*gazette_field_registry.values()))

    @classmethod
    def configure(cls, storage, bloom_filter=None, geohash_precision=DEFAULT_GEOHASH_PRECISION):
        cls.storage = storage
        if bloom_filter:
            cls.bloom_filter = bloom_filter
        cls.geohash_precision = geohash_precision

    @classmethod
    def expanded_street_address(cls, address):
        street_address_components = []

        house_number = (address.house_number or '').strip()
        if house_number:
            street_address_components.append(house_number)

        street = (address.street or '').strip()
        if street:
            street_address_components.append(street)

        surface_forms = set()
        if street_address_components:
            street_address = u' '.join(street_address_components)
            # the return value from expand

        return address_phrase_filter.expand_street_address(street_address)

    @classmethod
    def geohash(cls, address):
        geo = geohash.encode(address.latitude, address.longitude, cls.geohash_precision)
        neighbors = geohash.neighbors(geo)
        all_geo = [geo] + neighbors
        return all_geo

    @classmethod
    def gen_keys(cls, address):
        street_surface_forms = cls.expanded_street_address(address)
        
        if address.latitude and address.longitude:
            all_geo = cls.geohash(address)

            for geo, norm_address in product(all_geo, street_surface_forms):
                key = '|'.join([geo, norm_address])
                yield key


class VenueNearDupe(NearDupe):
    __entity_type__ = Venue.entity_type
    model = Venue