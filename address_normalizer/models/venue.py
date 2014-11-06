from address_normalizer.models.base import *
from address_normalizer.models.address import *

class Venue(Model):
	entity_type = 'venue'

	guid = StringType(default=random_guid)

	address = ModelType(Address)

	name = StringType()
