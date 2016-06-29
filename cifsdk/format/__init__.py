COLUMNS = ['tlp', 'lasttime', 'reporttime', 'itype', 'indicator', 'cc', 'asn', 'asn_desc', 'confidence', 'description',
           'tags', 'rdata', 'provider']
MAX_FIELD_SIZE = 30

from cifsdk.format.table import Table
from cifsdk.format.zcsv import Csv
from cifsdk.format.zjson import Json
FORMATS = {'table': Table, 'csv': Csv, 'json': Json}
