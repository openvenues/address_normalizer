import re
import six

from address_normalizer.text.encoding import *
from address_normalizer.utils.enum import *
from address_normalizer.text.util import *

import _scanner

# TODO: This duplicates the C code, better to regex the values directly from the file
class token_types(Enum):
    WORD = EnumValue(1, 'WORD')
    ABBREVIATION = EnumValue(2, 'ABBREVIATION')
    PHRASE = EnumValue(3, 'PHRASE')

    NUMBER = EnumValue(50, 'NUMBER')
    NUMERIC = EnumValue(51, 'NUMERIC')
    ORDINAL = EnumValue(52, 'ORDINAL')
    NUMERIC_RANGE = EnumValue(53, 'NUMERIC_RANGE')
    ORDINAL_RANGE = EnumValue(54, 'ORDINAL_RANGE')
    ROMAN_NUMERAL = EnumValue(55, 'ROMAN_NUMERAL')

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
    MDASH = EnumValue(111, 'MDASH')
    HYPHEN = EnumValue(112, 'HYPHEN')
    LPAREN = EnumValue(113, 'LPAREN')
    RPAREN = EnumValue(114, 'RPAREN')
    LBSQUARE = EnumValue(115, 'LBSQUARE')
    RBSQUARE = EnumValue(116, 'RBSQUARE')
    DOUBLE_QUOTE = EnumValue(117, 'DOUBLE_QUOTE')
    SINGLE_QUOTE = EnumValue(118, 'SINGLE_QUOTE')
    LEFT_DOUBLE_QUOTE = EnumValue(119, 'LEFT_DOUBLE_QUOTE')
    RIGHT_DOUBLE_QUOTE = EnumValue(120, 'RIGHT_DOUBLE_QUOTE')
    LEFT_SINGLE_QUOTE = EnumValue(121, 'LEFT_SINGLE_QUOTE')
    RIGHT_SINGLE_QUOTE = EnumValue(122, 'RIGHT_SINGLE_QUOTE')
    SLASH = EnumValue(123, 'SLASH')
    BACKSLASH = EnumValue(124, 'BACKSLASH')
    GREATER_THAN = EnumValue(125, 'GREATER_THAN')
    LESS_THAN = EnumValue(126, 'LESS_THAN')

    OTHER = EnumValue(200, 'OTHER')
    NEWLINE = EnumValue(301, 'NEWLINE')


PUNCTUATION_TOKEN_TYPE_MIN_VALUE = 100

CONTENT_TOKEN_TYPES = set([
    t for t in token_types if t.value < PUNCTUATION_TOKEN_TYPE_MIN_VALUE
])

padding = six.unichr(0) * 4

def tokenize(text):
    # Make sure the string is unicode and pad with null bytes
    text = safe_decode(text) + padding
    # The C function just returns the token type (integer), the start index and the length
    # so Python is free to create memoryviews etc. instead of slicing if needed
    return [(token_types[token_type], text[start:start+length])
                for token_type, start, length in _scanner.scan(text)]




