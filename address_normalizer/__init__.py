from flask import Flask

from . import config
from address_normalizer.views import init_views
from address_normalizer.deduping import *

def create_app(env, **kw):
    app = Flask(__name__)
    specified_config = kw.get('config')
    if specified_config:
        __import__('address_normalizer.' + specified_config)
    config.current_env = env
    conf = config.valid_configs.get(env)
    if not conf:
        sys.exit('Invalid config, choices are [%s]' % ','.join(valid_configs.keys()))

    app.config.from_object(conf)
    
    app.url_map.strict_slashes = False

    init_dbs(app)
    init_views(app)
   
    return app