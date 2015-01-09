# -*- coding: utf-8 -*-

import os
import glob
import string

import ujson as json

import unidecode
import unicodedata

from itertools import chain, product

from collections import *
from marisa_trie import BytesTrie

from address_normalizer.text.gazetteers import *
from address_normalizer.text.tokenize import *
from address_normalizer.text.numex import *
from address_normalizer.text.encoding import *
from address_normalizer.utils.enum import *

possessive_replacements = {"'s": "s",
                           "s'": "s",
                        }

def replace_possessive(word):
    return word[:-2] + possessive_replacements.get(word[-2:], word[-2:])

character_replacements = {
    0x2018: u"'",   # LEFT SINGLE QUOTATION MARK
    0x2019: u"'",   # RIGHT SINGLE QUOTATION MARK
    0x201c: u'"',   # LEFT DOUBLE QUOTATION MARK
    0x201d: u'"',   # RIGHT DOUBLE QUOTATION MARK
    0x201e: u'"',   # DOUBLE LOW-9 QUOTATION MARK
    0x2026: u'...', # HORIZONTAL ELLIPSIS
    0x0152: u'OE',  # LATIN CAPITAL LIGATURE OE
    0x0153: u'oe',   # LATIN SMALL LIGATURE OE
    0x00bc: u'1/4',  # VULGAR FRACTION ONE FOURTH
    0x00bd: u'1/2',  # VULGAR FRACTION ONE HALF
    0x00be: u'3/4',  # VULGAR FRACTION THREE FOURTHS    
    0x2153: u'1/3',  # VULGAR FRACTION ONE THIRD
    0x2154: u'2/3',  # VULGAR FRACTION TWO THIRDS
    0x00df: u'ss',   # LATIN SMALL LETTER SHARP S

    '-': u'-',       # HYPHEN-MINUS
    0x2010: u'-',    # HYPHEN
    0x2011: u'-',    # NON-BREAKING HYPHEN
    0x2012: u'-',    # FIGURE DASH
    0x2013: u'-',    # EN DASH
    0x2014: u'-',    # EM DASH
    0x2013: u'-',    # EN DASH
    0x2014: u'-',    # EM DASH
    0x2015: u'-',    # HORIZONTAL BAR
    0x2e17: u'-',    # DOUBLE OBLIQUE HYPHEN
    0x2e1a: u'-',    # HYPHEN WITH DIAERESIS
    0x301c: u'-',    # WAVE DASH
    0x3030: u'-',    # WAVY DASH
    0xfe31: u'-',    # PRESENTATION FORM FOR VERTICAL EM DASH
    0xfe32: u'-',    # PRESENTATION FORM FOR VERTICAL EN DASH
    0xfe58: u'-',    # SMALL EM DASH
    0xfe63: u'-',    # SMALL HYPHEN-MINUS
    0xff0d: u'-',    # FULLWIDTH HYPHEN-MINUS
}

def replace_chars(text):
    return text.translate(character_replacements)

# Normalizes ü=>u, å=>a, etc.
def strip_diacritics(s):
    return u''.join([c for c in unicodedata.normalize('NFKD', s) if unicodedata.category(c) != 'Mn' ])

# This is more advanced, strips diacritics but also converts e.g. 北亰 to Bei Jing
def convert_to_ascii(s):
    return unidecode.unidecode(s)

word_token_replacements = {
    0x002d: u' ',
    0x002e: u' ',
}

numeric_token_replacements = {
    0x002d: u'',
    0x002e: u'',
    0x0023: u'',
}


def scalar_transform(token_class, token, norm_tokens):
    if token_class in (token_types.WORD, token_types.ABBREVIATION) and any((roman_numeral_regex.match(t) for c, t in norm_tokens)):
        roman_numeral_tokens = [(token_types.ROMAN_NUMERAL, str(convert_roman_numeral(t))) if roman_numeral_regex.match(t) else (c,t) for c, t in norm_tokens]
        return roman_numeral_tokens
    elif token_class == token_types.NUMERIC:
        return [(token_class, token.translate(numeric_token_replacements).lower().strip())]

def norm_token(token_class, token):
    if token_class in (token_types.WORD, token_types.ABBREVIATION, token_types.NUMERIC):
        translated = token.translate(word_token_replacements).lower()
        if translated == token:
            word_tokens = [(token_class, token)]
        else:
            word_tokens = tokenize(translated)

        return word_tokens
    else:
        return [(token_class, token)]

def clean(text, ascii=True, remove_accents=False):
    text = safe_decode(text)
    text = replace_chars(text)
    if ascii:
        text = convert_to_ascii(text)
    elif remove_accents:
        text = strip_accents(text)
    return text


class PhraseFilter(object):
    def __init__(self):
        self.configured = False

    def configure(self, *args, **kw):
        pass

    serialize = json.dumps
    deserialize = json.loads

    def filter(self, tokens):
        def return_item(item):
            return item[0], item[1:], []

        if not tokens:
            return
    
        SENTINEL = None

        ent = []
        ent_tokens = []

        norm_tokens = [tuple(item[:-1]) + (replace_possessive(item[-1].lower()), item[-1].lower()) for item in tokens]
        
        queue = deque(norm_tokens + [(SENTINEL,)*3])
        skip_until = 0

        trie = self.trie
        
        while queue:
            item = queue.popleft()
            n, t = item[-2:]
            
            if t is not SENTINEL and trie.has_keys_with_prefix(u' '.join(ent_tokens + [t])):
                ent.append(item)
                ent_tokens.append(item[-1])
            elif t is not SENTINEL and n != t and trie.has_keys_with_prefix(u' '.join(ent_tokens + [n])):
                ent.append(item[:-1] + (n,) )
                ent_tokens.append(n)
            elif ent_tokens:
                res = trie.get(u' '.join(ent_tokens)) or None
                if res is not None:
                    yield (token_types.PHRASE, ent, map(self.deserialize, res))
                    queue.appendleft(item)
                    ent = []
                    ent_tokens = []
                elif len(ent_tokens) == 1:
                    yield return_item(ent[0])
                    ent = []
                    ent_tokens = []
                    queue.appendleft(item)
                else:
                    have_phrase = False
                    
                    for i in xrange(len(ent)-1, 0, -1):
                        remainder = ent[i:]
                        res = trie.get(u' '.join([e[-1] for e in ent[:i]])) or None
                        if res is not None:
                            yield (token_types.PHRASE, ent[:i], map(self.deserialize, res))
                            have_phrase = True
                            break
                    
                    if not have_phrase:
                        yield return_item(ent[0])
                    
                    todos = list(remainder)
                    todos.append(item)
                    queue.extendleft(reversed(todos))
                    
                    ent = []
                    ent_tokens = []      
            elif t is not SENTINEL:
                yield return_item(item)



BEGIN = 'B'
IN = 'I'
LAST = 'L'
OUT = 'O'
UNIQUE = 'U'

def bilou_encoding(i, length):
    if length == 1:
        return UNIQUE
    elif i > 0 and i < length-1:
        return IN
    elif i == 0:
        return BEGIN
    elif i == length-1:
        return LAST

tag_sequences = {
    BEGIN: set([IN, LAST]),
    IN: set([IN, LAST]),
    LAST: set([BEGIN, UNIQUE, OUT]),
    UNIQUE: set([UNIQUE, BEGIN, OUT]),
    OUT: set([OUT, BEGIN, UNIQUE]),
}

beginnings = set([BEGIN, UNIQUE])
endings = set([LAST, UNIQUE])

def gazetteers_for(*fields):
    return list(chain(*[gazette_field_registry[f] for f in fields]))

class AddressPhraseFilter(PhraseFilter):
    all_gazetteers = []
    street_gazetteers = []

    def configure(self, base_dir):
        kvs = []

        for g in gazetteers:
            g.configure(base_dir)
            sub_gazettes = [g] if not g.multi else g.gazetteers
            for g in sub_gazettes:
                f = open(g.path)
                for line in f:
                    if not line.strip() or line.strip().startswith('#'):
                        continue
                    surface_forms = map(string.strip, line.rstrip().split(g.separator))
                    canonical, other = surface_forms[0], surface_forms[1:]

                    kvs.append((safe_decode(canonical), self.serialize((canonical, g.filename, g.classification.value))))
                    for o in other:
                        kvs.append((safe_decode(o), self.serialize((canonical, g.filename, g.classification.value))))

        self.trie = BytesTrie(kvs)

        self.all_gazetteers = list(chain(*gazette_field_registry.values()))
        self.street_gazetteers = list(chain(*[gazette_field_registry[f] for f in (
                                      address_fields.NAME, address_fields.HOUSE_NUMBER, 
                                      address_fields.STREET)]))

        self.configured = True

    def expand_surface_forms(self, component, dictionary_types=None, normalize_numex=False):
        dictionary_types = set([d.classification for d in (dictionary_types or self.all_gazetteers)] + [dictionaries.ANY])
        if not component.strip():
            return []
        component = clean(component)
        tokens = tokenize(component)

        if normalize_numex:
            tokens = convert_numeric_expressions(tokens)

        norm_tokens = [norm_token(c,t) for c, t in tokens]
        norm_token_map = []
        i = 0
        for i, t in enumerate(norm_tokens):
            norm_token_map.extend([i]*len(t))

        phrase_tokens = []

        possible_expansions = []
        i = 0
        for c, t, data in self.filter(list(chain(*norm_tokens))):
            if c == token_types.PHRASE:
                valid_expansions = set([(dictionaries.registry[val], canonical) for canonical, filename, val in data if val in dictionary_types])
                len_t = len(t)
                if valid_expansions:
                    phrase_tokens.extend([[(bilou_encoding(j, len_t), classification, tok[-1], canonical) for classification, canonical in valid_expansions] for j, tok in enumerate(t)])
                else:
                    phrase_tokens.extend([[(OUT, tok[0], tok[-1], None)] for tok in t])
            else:
                phrase_tokens.append([(OUT, c, t[-1], None)])

        possible_expansions.append(phrase_tokens)

        single_tokens = []
        any_differing_tokens = False
        skip_until = 0
        for i, (ti, p) in enumerate(zip(norm_token_map, phrase_tokens)):
            if i < skip_until:
                continue
            norm = norm_tokens[ti]
            token_class, token = tokens[ti]
            token_extensions = p[:] if len(norm) == 1 else []
            scalar_tokens = scalar_transform(token_class, token, norm)
            if not scalar_tokens:
                pass
            elif len(scalar_tokens) > 1 or (len(scalar_tokens) < len(norm)):
                token_extensions.extend([(OUT, c, t, None) for c, t in scalar_tokens])
                skip_until = i + len(scalar_tokens) + 1
                any_differing_tokens = True
            elif scalar_tokens != tokens:
                token_extensions.append((OUT, scalar_tokens[0][0], scalar_tokens[0][1], None))
                any_differing_tokens = True
            single_tokens.append(token_extensions)

        if any_differing_tokens:
           possible_expansions.append(single_tokens)


        return possible_expansions
    
    def join_phrase(self, expansion):
        valid_tokens = []
        num_tokens = len(expansion)
        for i, (phrase_membership, token_class, token, canonical) in enumerate(expansion):
            if phrase_membership != OUT and token_class is dictionaries.UNIT and i < num_tokens-1 and any(map(partial(operator.is_, expansion[i+1][1]), [token_types.NUMBER, token_types.NUMERIC])):
                continue

            if phrase_membership == OUT and token_class in CONTENT_TOKEN_TYPES:
                valid_tokens.append(token)
            elif phrase_membership in (UNIQUE, BEGIN):
                valid_tokens.append(canonical)

        return u' '.join(valid_tokens)

    def expand_string(self, s, *args, **kw):
        return set(map(self.join_phrase, chain(*(product(*c) for c in self.expand_surface_forms(safe_decode(s), *args, **kw)))))


    def expand_street_address(self, street_address):
        return self.expand_string(street_address, self.street_gazetteers, normalize_numex=True)

    def expand_full_address(self, address):
        return self.expand_string(address, self.all_gazetteers, normalize_numex=True)

address_phrase_filter = AddressPhraseFilter()
address_phrase_filter.configure(DEFAULT_GAZETTEER_DIR)

