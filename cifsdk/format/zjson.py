import json

from cifsdk.format.plugin import Plugin

class Json(Plugin):

    def __repr__(self):
        output = []
        
        for obs in reversed(self.data):
            r = dict()
            for c in self.cols:
                y = obs.get(c, u'')
                if type(y) is list:
                    y = u','.join(y)
                
                r[c] = y
                
            output.append(r)
            
        return json.dumps(self.data)
