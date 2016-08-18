import csv
from cifsdk.constants import PYVERSION

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from cifsdk.format.plugin import Plugin


class Csv(Plugin):

    def __repr__(self):
        output = StringIO()
        
        csvWriter = csv.DictWriter(output, self.cols, quoting=csv.QUOTE_ALL)
        csvWriter.writeheader()

        for obs in reversed(self.data):
            r = dict()
            for c in self.cols:
                y = obs.get(c, u'')
                if type(y) is list:
                    y = u','.join(y)

                if PYVERSION < 3:
                    y = unicode(y).replace('\n', r'\\n')
                    r[c] = y.encode('utf-8', 'ignore')
                else:
                    r[c] = y.replace('\n', r'\\n')
                
            csvWriter.writerow(r)
        
        return output.getvalue().strip('\r\n')
