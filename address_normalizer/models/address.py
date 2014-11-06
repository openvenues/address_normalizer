from address_normalizer.models.base import *

class Address(Model):
	entity_type = 'address'
	
	guid = StringType(default=random_guid)

	house_name = StringType()
	house_number = StringType()
	street = StringType()
	locality = StringType()
	region = StringType()
	country = StringType()
	postal_code = StringType()

	latitude = FloatType()
	longitude = FloatType()



