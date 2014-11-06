from uuid import uuid4

def random_guid():
    return str(uuid4()).replace('-','')