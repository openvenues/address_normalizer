#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import unittest

from address_normalizer import expand_street_address
from address_normalizer.text.encoding import safe_encode, safe_decode

street_test_cases = (
    # input, expected output
    ('MAPLE ST.', 'maple street'),
    ('ST ISIDORE DR', 'saint isidore drive'),
    ('ST. Sebastian ST', 'saint sebastian street'),
    ("St John's St.", 'saint johns street'),
    ('MORNINGTON CR', 'mornington crescent'),
    ('Cércle rouge', 'cercle rouge'),
    ('Third Street', '3rd street'),
)

dupe_test_cases = (
    # addresses should share at least one expansion in common
    ('30 West Twenty-sixth Street Floor Number 7',
     '30 W 26th St Fl #7'),
    ('123 Dr. Martin Luther King Jr. Dr.',
     '123 Doctor Martin Luther King Junior Drive')
)


class TestNormalization(unittest.TestCase):
    def test_street_name(self):
        for original, expected in street_test_cases:
            self.assertTrue(expected in expand_street_address(original))

    def test_dupes(self):
        for a1, a2 in dupe_test_cases:
            self.assertTrue(expand_street_address(a1) &
                            expand_street_address(a2))

    def test_diacritics(self):
        orig = 'cércle rouge'
        self.assertTrue(orig in expand_street_address(orig, remove_accents=False))
        self.assertTrue('cercle rouge' in expand_street_address(orig, remove_accents=True))

    def test_decoding(self):
        self.assertEqual(safe_decode(b'é'), 'é')
        self.assertEqual(safe_decode('é'), 'é')
        self.assertEqual(safe_decode(1), '1')

    def test_encoding(self):
        self.assertEqual(safe_encode('é'), b'é')
        self.assertEqual(safe_encode(b'é'), b'é')
        self.assertEqual(safe_encode(1), b'1')

if __name__ == '__main__':
    unittest.main()
