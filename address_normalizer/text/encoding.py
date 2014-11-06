import six

def safe_decode(text, encoding='utf-8', errors='strict'):
    if isinstance(text, six.text_type):
        return text
    
    if isinstance(text, (six.string_types, six.binary_type)):
        return text.decode(encoding, errors)    
    else:
        raise TypeError('{} cannot be decoded'.format(type(text)))

def safe_encode(text, incoming=None, encoding='utf-8', errors='strict'):
    if not isinstance(text, (six.string_types, six.binary_type)):
        raise TypeError('{} cannot be decoded'.format(type(text)))
    
    if isinstance(text, six.text_type):
        return text.encode(encoding, errors)
    else:
        if hasattr(incoming, 'lower'):
            incoming = incoming.lower()
        if hasattr(encoding, 'lower'):
            encoding = encoding.lower()

        if text and encoding != incoming:
            text = safe_decode(text, encoding, errors)
            return text.encode(encoding, errors)
        else:
            return text