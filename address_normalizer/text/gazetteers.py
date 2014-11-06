import os
import glob

from collections import *

from address_normalizer.utils.enum import *

this_dir = os.path.realpath(os.path.dirname(__file__))

DEFAULT_GAZETTEER_DIR = os.path.join(this_dir, 'dictionaries')

class dictionaries(Enum):
    ANY = EnumValue(1, 'ANY')
    STREET_NAME = EnumValue(2, 'STREET_NAME')
    STREET_TYPE = EnumValue(3, 'STREET_TYPE')
    CONCATENATED_SUFFIX = EnumValue(4, 'CONCATENATED_SUFFIX')
    QUALIFIER = EnumValue(5, 'QUALIFIER')
    PRE_DIRECTIONAL = EnumValue(6, 'PRE_DIRECTIONAL')
    SAINT = EnumValue(7, 'SAINT')
    NULL = EnumValue(8, 'NULL')
    LEVEL = EnumValue(9, 'LEVEL')
    UNIT = EnumValue(10, 'UNIT')
    PO_BOX = EnumValue(11, 'PO_BOX')

    PROPER_NAME = EnumValue(50, 'PROPER_NAME')
    PERSONAL_TITLE = EnumValue(51, 'PERSONAL_TITLE')
    PERSONAL_SUFFIX = EnumValue(52, 'PERSONAL_SUFFIX')
    ACADEMIC_DEGREE = EnumValue(53, 'ACADEMIC_DEGREE')

    LOCALITY = EnumValue(100, 'LOCALITY')
    REGION = EnumValue(101, 'REGION')
    POST_CODE = EnumValue(102, 'POST_CODE')
    COUNTRY = EnumValue(103, 'COUNTRY')


class address_fields(Enum):
    ANY = EnumValue(1, 'ANY')
    NAME = EnumValue(2, 'NAME')
    HOUSE_NUMBER = EnumValue(3, 'HOUSE_NUMBER')
    STREET = EnumValue(4, 'STREET')
    LOCALITY = EnumValue(5, 'LOCALITY')
    REGION = EnumValue(6, 'REGION')
    COUNTRY = EnumValue(7, 'COUNTRY')
    POSTAL_CODE = EnumValue(8, 'POSTAL_CODE')

gazette_registry = {}
gazette_field_registry = defaultdict(list)


class Gazetteer(object):
    configured = False
    multi = False

    def __init__(self, filename, classification, fields, separator='|'):
        self.filename, self.extension = os.path.splitext(filename)
        self.classification = classification
        self.separator = separator
        self.fields = fields

    def configure(self, base_dir):
        self.path = os.path.join(base_dir, self.filename + self.extension)
        gazette_registry[self.path] = self
        for f in self.fields:
            gazette_field_registry[f].append(self)
        self.configured = True

    def get_files(self):
        if not self.configured:
            raise ValueError('Gazetteer has not been configured')


class GlobGazetteer(Gazetteer):
    multi = True

    def __init__(self, pattern, classification, fields, separator='|'):
        self.classification = classification
        self.separator = separator
        self.pattern = pattern
        self.fields = fields
        self.gazetteers = []

    def configure(self, base_dir):
        for f in glob.glob(os.path.join(base_dir, self.pattern)):
            g = Gazetteer(os.path.basename(f), self.classification, fields=self.fields, separator=self.separator)
            g.configure(base_dir)
            self.gazetteers.append(g)


# fields args are using set literal notation e.g. {"foo", "bar"}
gazetteers = [
    Gazetteer('academic_degrees.txt', dictionaries.ACADEMIC_DEGREE, fields={address_fields.NAME}),
    Gazetteer('addr_misc.txt', dictionaries.ANY, fields={address_fields.ANY}),
    Gazetteer('address_qualifiers.txt', dictionaries.QUALIFIER, fields={address_fields.STREET}),
    Gazetteer('australian_states.txt', dictionaries.REGION, fields={address_fields.REGION}),
    Gazetteer('canadian_provinces.txt', dictionaries.REGION, fields={address_fields.REGION}),
    Gazetteer('countries.txt', dictionaries.COUNTRY, fields={address_fields.COUNTRY}),
    Gazetteer('level_types.txt', dictionaries.LEVEL, fields={address_fields.HOUSE_NUMBER, address_fields.STREET}),
    Gazetteer('no_number.txt', dictionaries.NULL, fields={address_fields.HOUSE_NUMBER, address_fields.STREET}),
    Gazetteer('nulls.txt', dictionaries.NULL, fields={address_fields.ANY}),
    Gazetteer('post_office.txt', dictionaries.PO_BOX, fields={address_fields.HOUSE_NUMBER, address_fields.STREET}),
    Gazetteer('proper_names.txt', dictionaries.PROPER_NAME, fields={address_fields.NAME}),
    Gazetteer('saints.txt', dictionaries.SAINT, fields={address_fields.NAME, address_fields.STREET}),
    Gazetteer('street_types.txt', dictionaries.STREET_TYPE, fields={address_fields.STREET}),
    Gazetteer('personal_titles.txt', dictionaries.PERSONAL_TITLE, fields={address_fields.NAME, address_fields.STREET}),
    Gazetteer('personal_suffixes.txt', dictionaries.PERSONAL_SUFFIX, fields={address_fields.NAME, address_fields.STREET}),
    Gazetteer('uk_counties.txt', dictionaries.REGION, fields={address_fields.REGION}),
    Gazetteer('unit_types.txt', dictionaries.UNIT, fields={address_fields.HOUSE_NUMBER, address_fields.STREET}),
    Gazetteer('us_states.txt', dictionaries.REGION, fields={address_fields.REGION}),
    GlobGazetteer('postal_codes.*', dictionaries.POST_CODE, fields={address_fields.POSTAL_CODE}),
]
