from ._version import get_versions
VERSION = get_versions()['version']
del get_versions

import os.path
import tempfile
import sys
from csirtg_indicator.constants import COLUMNS

PYVERSION = 2
if sys.version_info > (3,):
    PYVERSION = 3

TEMP_DIR = os.path.join(tempfile.gettempdir())
RUNTIME_PATH = os.environ.get('CIF_RUNTIME_PATH', TEMP_DIR)
RUNTIME_PATH = os.path.join(RUNTIME_PATH)

# Logging stuff
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s[%(lineno)s][%(threadName)s] - %(message)s'

LOGLEVEL = 'ERROR'
LOGLEVEL = os.environ.get('CIF_LOGLEVEL', LOGLEVEL).upper()

CONFIG_PATH = os.environ.get('CIF_CONFIG_PATH', os.path.join(os.getcwd(), 'cif.yml'))
if not os.path.isfile(CONFIG_PATH):
    CONFIG_PATH = os.path.join(os.path.expanduser('~'), '.cif.yml')

# address stuff

REMOTE_ADDR = 'http://localhost:5000'
REMOTE_ADDR = os.environ.get('CIF_REMOTE_ADDR', REMOTE_ADDR)

ROUTER_ADDR = "ipc://{}".format(os.path.join(RUNTIME_PATH, 'router.ipc'))
ROUTER_ADDR = os.environ.get('CIF_ROUTER_ADDR', ROUTER_ADDR)

SEARCH_LIMIT = os.environ.get('CIF_SEARCH_LIMIT', 500)
FEED_LIMIT = os.environ.get('CIF_FEED_LIMIT', 50000)
FEED_DAYS_LIMIT = os.environ.get('CIF_FEED_DAYS_LIMIT', 21)

TOKEN = os.environ.get('CIF_TOKEN', None)
FORMAT = os.environ.get('CIF_FORMAT', 'table')

ADVANCED = os.getenv('CIF_ADVANCED')

COLUMNS = COLUMNS
MAX_FIELD_SIZE = 30
