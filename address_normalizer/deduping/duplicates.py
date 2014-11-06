
dupe_registry = {}

class DupeMeta(type):
    def __init__(cls, name, bases, dict_):
        if 'abstract' not in dict_:
            dupe_registry[cls.__entity_type__] = cls

class Dupe(object):
    abstract = True
    __metaclass__ = DupeMeta

class AddressDupe(Dupe):
    __entity_type__ = 'address'
    
    # Always return True
    @classmethod
    def is_dupe(cls, address_1, address_2):
    	return True