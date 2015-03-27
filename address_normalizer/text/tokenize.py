import re
import six

from address_normalizer.text.encoding import *
from address_normalizer.utils.enum import *

from address_normalizer.text import _scanner


# TODO: This duplicates the C code, regex the values directly from header
class token_types(Enum):
    END = EnumValue(0, 'END')

    WORD = EnumValue(1, 'WORD')
    ABBREVIATION = EnumValue(2, 'ABBREVIATION')
    IDEOGRAPHIC_CHAR = EnumValue(3, 'IDEOGRAPHIC_CHAR')
    PHRASE = EnumValue(4, 'PHRASE')

    EMAIL = EnumValue(20, 'EMAIL')
    URL = EnumValue(21, 'URL')
    US_PHONE = EnumValue(22, 'US_PHONE')
    INTL_PHONE = EnumValue(23, 'INTL_PHONE')

    NUMERIC = EnumValue(50, 'NUMERIC')
    ORDINAL = EnumValue(51, 'ORDINAL')
    ROMAN_NUMERAL = EnumValue(52, 'ROMAN_NUMERAL')
    IDEOGRAPHIC_NUMBER = EnumValue(53, 'IDEOGRAPHIC_NUMBER')

    PERIOD = EnumValue(100, 'PERIOD')
    EXCLAMATION = EnumValue(101, 'EXCLAMATION')
    QUESTION_MARK = EnumValue(102, 'QUESTION_MARK')
    COMMA = EnumValue(103, 'COMMA')
    COLON = EnumValue(104, 'COLON')
    SEMICOLON = EnumValue(105, 'SEMICOLON')
    PLUS = EnumValue(106, 'PLUS')
    AMPERSAND = EnumValue(107, 'AMPERSAND')
    AT_SIGN = EnumValue(108, 'AT_SIGN')
    POUND = EnumValue(109, 'POUND')
    ELLIPSIS = EnumValue(110, 'ELLIPSIS')
    DASH = EnumValue(111, 'DASH')
    BREAKING_DASH = EnumValue(112, 'BREAKING_DASH')
    HYPHEN = EnumValue(113, 'HYPHEN')
    PUNCT_OPEN = EnumValue(114, 'PUNCT_OPEN')
    PUNCT_CLOSE = EnumValue(115, 'PUNCT_CLOSE')
    DOUBLE_QUOTE = EnumValue(119, 'DOUBLE_QUOTE')
    SINGLE_QUOTE = EnumValue(120, 'SINGLE_QUOTE')
    OPEN_QUOTE = EnumValue(121, 'OPEN_QUOTE')
    CLOSE_QUOTE = EnumValue(122, 'CLOSE_QUOTE')
    SLASH = EnumValue(124, 'SLASH')
    BACKSLASH = EnumValue(125, 'BACKSLASH')
    GREATER_THAN = EnumValue(126, 'GREATER_THAN')
    LESS_THAN = EnumValue(127, 'LESS_THAN')

    OTHER = EnumValue(200, 'OTHER')

    WHITESPACE = EnumValue(300, 'WHITESPACE')
    NEWLINE = EnumValue(301, 'NEWLINE')


PUNCTUATION_TOKEN_TYPE_MIN_VALUE = 100

CONTENT_TOKEN_TYPES = set([
    t for t in token_types if t.value < PUNCTUATION_TOKEN_TYPE_MIN_VALUE
])

padding = six.unichr(0) * 4


def tokenize(text):
    # Make sure the string is unicode and pad with null bytes
    text = safe_decode(text)
    # The C function just returns the token type (integer), the start index and the length
    # so Python is free to create memoryviews etc. instead of slicing if needed
    return [(token_types[token_type], token)
            for token_type, token in _scanner.scan(text)]
