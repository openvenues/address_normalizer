from .text.normalize import address_phrase_filter


# Valid kwargs: normalize_numex=True, to_ascii=False, remove_accents=True
def expand_full_address(address, **kw):
    return address_phrase_filter.expand_full_address(address, **kw)


def expand_street_address(street_address, **kw):
    return address_phrase_filter.expand_street_address(street_address, **kw)


# Stubs
def normalize_street_address(street_address, **kw):
    return list(expand_street_address(street_address, **kw))[0]


def normalize_full_address(address, **kw):
    return list(expand_full_address(address))[0]
