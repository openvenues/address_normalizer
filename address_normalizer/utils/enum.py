

class EnumValue(object):
    def __init__(self, value, description):
        self.value = value
        self.description = description

    def __hash__(self):
        return self.value

    def __cmp__(self, other):
        if isinstance(other, EnumValue):
            return self.value.__cmp__(other.value)
        else:
            return self.value.__cmp__(other)

    def __unicode__(self):
        return self.description

    def __str__(self):
        return self.description

    def __repr__(self):
        return self.description

class EnumMeta(type):
    def __init__(cls, name, bases, dict_):
        cls.registry = cls.registry.copy()
        for k, v in dict_.iteritems():
            if isinstance(v, EnumValue) and v not in cls.registry:
                cls.registry[v.value] = v
        return super(EnumMeta, cls).__init__(name, bases, dict_)

    def __iter__(cls):
        return cls.registry.itervalues()

    def __getitem__(cls, key):
        return cls.registry[key]

class Enum(object):
    __metaclass__ = EnumMeta
    registry = {}

    @classmethod
    def from_id(cls, value):
        try:
            return cls.registry[value]
        except KeyError:
            raise ValueError('Invalid value for %s: %s' % cls.__name__, value)