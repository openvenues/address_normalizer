import re
import string

import sys

from itertools import chain

from address_normalizer.text.tokenize import *

unit = {
        # Unit
        'zero': 0,
        'oh': 0,
        'one': 1,
        'two': 2,
        'three': 3,
        'four': 4, 
        'five': 5,
        'six': 6,
        'seven': 7,
        'eight': 8,
        'nine': 9,
}
        
unit_ordinals = {
        'first': 1,
        'second': 2,
        'third': 3,
        'forth': 4, 
        'fourth': 4,
        'fifth': 5,
        'sixth': 6,
        'seventh': 7,
        'eighth': 8,
        'ninth': 9,
}

teens = {
        # Teens
        'ten': 10,
        'eleven': 11,
        'twelve': 12,
        'thirteen': 13,
        'fourteen': 14,
        'fifteen': 15,
        'sixteen': 16,
        'seventeen': 17,
        'eighteen': 18,
        'nineteen': 19,
}

teen_ordinals = {
        'tenth': 10,
        'eleventh': 11,
        'twelfth': 12,
        'twelveth': 12,
        'thirteenth': 13,
        'fourteenth': 14,
        'fifteenth': 15,
        'sixteenth': 16,
        'seventeenth': 17,
        'eighteenth': 18,
        'nineteenth': 19,
}

tens = {
        'twenty': 20,
        'thirty': 30,
        'forty': 40,
        'fourty': 40,
        'fifty': 50,
        'sixty': 60,
        'seventy': 70,
        'eighty': 80,
        'ninety': 90,
}


tens_ordinals = {
    'twentieth': 20,
    'thirtieth': 30,
    'fortieth': 40,
    'fourtieth': 40,
    'fiftieth': 50,
    'sixtieth': 60,
    'seventieth': 70,
    'eightieth': 80,
    'ninetieth': 90
}

hundreds = {
    'hundred': 100
}

hundreds_ordinals = {
    'hundredth': 100
}

thousands = {
    'thousand': 1000
}

thousands_ordinals = {
    'thousandth': 1000
}


ordinal_words = {}
numex = {}
post_modifiers = {}
numex.update(unit)
numex.update(unit_ordinals)
ordinal_words.update(unit_ordinals)
numex.update(teens)
numex.update(teen_ordinals)
ordinal_words.update(teen_ordinals)
numex.update(tens)
numex.update(tens_ordinals)
ordinal_words.update(tens_ordinals)
numex.update(hundreds)
numex.update(hundreds_ordinals)
post_modifiers.update(hundreds)
post_modifiers.update(hundreds_ordinals)
ordinal_words.update(hundreds_ordinals)
numex.update(thousands)
numex.update(thousands_ordinals)
post_modifiers.update(thousands)
post_modifiers.update(thousands_ordinals)


roman_numerals = (('m',  1000),
                   ('cm', 900),
                   ('d',  500),
                   ('cd', 400),
                   ('c',  100),
                   ('xc', 90),
                   ('l',  50),
                   ('xl', 40),
                   ('x',  10),
                   ('ix', 9),
                   ('v',  5),
                   ('iv', 4),
                   ('i',  1))

roman_numeral_regex = re.compile('^M?M?M?(?:CM|CD|D?C?C?C?)(?:XC|XL|L?X?X?X?)(?:IX|IV|V?I?I?I?)$', re.I)

def convert_roman_numeral(s):
    result = 0
    index = 0
    s = s.lower()

    for numeral, integer in roman_numerals:
        while s[index:index+len(numeral)] == numeral:
            result += integer
            index += len(numeral)
    return result

def is_roman_numeral(word):
    return bool(roman_numeral_regex.match(word))

ordinal_suffixes = {
    0: u'th',
    1: u'st',
    2: u'nd',
    3: u'rd',
    4: u'th',
    5: u'th',
    6: u'th',
    7: u'th',
    8: u'th',
    9: u'th',
}

def parse_numex(tokens):
    numbers = []
    number = []
    prev_magnitude = sys.maxint
    start_index = -1
    token_map = []

    for i, t in enumerate(tokens):
        token_map.extend((i, tok) for tok in t.split('-'))

    for i, t in token_map:
        t = t.lower()

        num = numex.get(t, None)
        if number and t in post_modifiers:
            number[-1] *= num
        elif num is not None and num/10 < prev_magnitude and number:
            number[-1] += num
        elif num is not None:
            if not number:
                start_index = i
            number.append(num)
        else:
            if number and i > prev_i:
                numbers.append(((start_index, i-1, u''.join(map(str, number)), False)))
                number = []

        prev_magnitude = num/10 if num is not None else sys.maxint

        if t in ordinal_words:
            num_str = u''.join(map(str, number))
            num_str += ordinal_suffixes[int(num_str[-1])]
            numbers.append(((start_index, i, num_str, True)))
            number = []
            prev_magnitude = sys.maxint

        prev_i = i

    if number and num:
        numbers.append(((start_index, i, u''.join(map(str, number)), False)))
 
    return numbers

def convert_numeric_expressions(tokens):
    numexes = parse_numex([t for c, t in tokens])
    last_end = 0 
    new_tokens = []
    for start, end, token, is_ordinal in numexes:
        new_tokens.extend(tokens[last_end:start])
        token_type = token_types.NUMBER if not is_ordinal else token_types.ORDINAL
        new_tokens.append((token_type, token))
        last_end = end+1

    new_tokens.extend(tokens[last_end:])
    return new_tokens