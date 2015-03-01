import csv
import os

from address_normalizer.polygons.index import *
from address_normalizer.text.language import *

this_dir = os.path.realpath(os.path.dirname(__file__))
language_dir = os.path.join(this_dir, os.pardir, os.pardir,
                            'data', 'language')
country_language_dir = os.path.join(language_dir, 'countries')
regional_language_dir = os.path.join(language_dir, 'regional')


class LanguagePolygonIndex(RTreePolygonIndex):

    @classmethod
    def create_from_shapefiles(cls,
                               admin0_shapefile,
                               admin1_shapefile,
                               admin1_region_file,
                               output_dir,
                               index_filename=DEFAULT_INDEX_FILENAME,
                               polys_filename=DEFAULT_POLYS_FILENAME):

        init_languages()
        index = cls(save_dir=output_dir, index_filename=index_filename)

        i = 0

        '''
        Ordering of the files is important here is important as we want to match
        the most granular admin polygon first for regional languages. Currently 
        most regional languages as they would apply to street signage are regional in
        terms of an admin 1 level (states, provinces, regions)
        '''
        for input_file in (admin0_shapefile, admin1_region_file, admin1_shapefile):
            f = fiona.open(input_file)

            for rec in f:
                if not rec or not rec.get('geometry') or 'type' not in rec['geometry']:
                    continue

                country = rec['properties']['qs_iso_cc'].lower()
                properties = rec['properties']

                admin_level = properties['qs_level']

                if admin_level == 'adm1':
                    name_key = 'qs_a1'
                    code_key = 'qs_a1_lc'
                elif admin_level == 'adm1_region':
                    name_key = 'qs_a1r'
                    code_key = 'qs_a1r_lc'
                elif admin_level != 'adm0':
                    continue

                if admin_level != 'adm0':
                    admin1 = properties.get(name_key)
                    admin1_code = properties.get(code_key)

                    regional_lang = None
                    is_default = None
                    if name_key:
                        regional_lang, is_default = regional_languages.get((country, name_key, admin1), (None, None))

                    if code_key and not regional_lang:
                        regional_lang, is_default = regional_languages.get((country, code_key, admin1_code), (None, None))

                    if not regional_lang:
                        continue

                    languages = [(lang, is_default) for lang in regional_lang.split(',')]
                else:
                    languages = official_languages[country].items()
                    overrides = road_language_overrides.get(country)
                    if overrides and overrides.values()[0]:
                        languages = overrides.items()
                    elif overrides:
                        languages.extend(overrides.items())

                properties['languages'] = [{'lang': lang, 'default': default}
                                           for lang, default in languages]

                poly_type = rec['geometry']['type']
                if poly_type == 'Polygon':
                    poly = Polygon(rec['geometry']['coordinates'][0])
                    index.index_polygon(i, poly)
                    index.add_polygon(poly, dict(rec['properties']))
                elif poly_type == 'MultiPolygon':
                    polys = []
                    for coords in rec['geometry']['coordinates']:
                        poly = Polygon(coords[0])
                        polys.append(poly)
                        index.index_polygon(i, poly)

                    index.add_polygon(MultiPolygon(polys), dict(rec['properties']))
                else:
                    continue

                i += 1
        return index
