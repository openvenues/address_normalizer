all:: address_normalizer/text/_scanner.re address_normalizer/text/scanner.c

address_normalizer/text/_scanner.re::
	re2c -F -s -b -x -o address_normalizer/text/scanner.c address_normalizer/text/_scanner.re
