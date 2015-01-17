#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest

from address_normalizer import normalize_street_address

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
            self.assertTrue(expected in normalize_street_address(original))

    def test_dupes(self):
        for a1, a2 in dupe_test_cases:
            self.assertTrue(normalize_street_address(a1) &
                            normalize_street_address(a2))

if __name__ == '__main__':
    unittest.main()
