REMOVE_ALL = """
	MATCH (n)
	OPTIONAL MATCH (n)-[r]-()
	DELETE n,r
"""

class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
   def __getattr__(self, attr):
       return getattr(self.stream, attr)

import sys
sys.stdout = Unbuffered(sys.stdout)

def replace_keys(row):
	new = {}
	for key,val in row.items():
		new[key.lower().replace('@','')] = val
	return new