import os, sys

from setuptools import setup, Extension, find_packages

def main():
    setup(
        name='address_normalizer',
        version='0.2',
        install_requires = [
            'six',
            'ujson',
	        'leveldb',
            'python-geohash',
            'marisa-trie',
	        'schematics',
	        'unidecode',
        ],
	    ext_modules = [
            Extension('address_normalizer.text._scanner',
                      sources = ['address_normalizer/text/scanner.c'],
            )
        ],
        packages=find_packages(),
        include_package_data=True,
        zip_safe=False,
        url='http://mapzen.com',
        description='Fast address standardization and deduplication',
        license='MIT License',
        maintainer='mapzen.com',
        maintainer_email='pelias@mapzen.com'
    )

if __name__ == '__main__':
    main()
