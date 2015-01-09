from .text.normalize import address_phrase_filter


def normalize_full_address(address):
    return address_phrase_filter.expand_full_address(address)

def normalize_street_address(street_address):
    return address_phrase_filter.expand_street_address(street_address)