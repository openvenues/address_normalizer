from itertools import *
from schematics.models import Model as DictSchema
from schematics.types import *

from schematics.types.compound import ModelType

from schematics.exceptions import ModelConversionError

from address_normalizer.utils.guid import *

class Model(DictSchema):	
	guid = StringType(default=random_guid)
