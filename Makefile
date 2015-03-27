all:: address_normalizer/text/_scanner.re address_normalizer/text/scanner.c

address_normalizer/text/_scanner.re::
	re2c -F -s -b -8 -o address_normalizer/text/scanner.c address_normalizer/text/_scanner.re
