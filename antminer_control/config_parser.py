import json
from collections import OrderedDict

CONF_FILE = 'cgminer.conf'
OUTPUT_FILE = 'test.conf'

with open(CONF_FILE, 'r') as f:
    conf = json.loads(f.read(), object_pairs_hook=OrderedDict)

print(conf['bitmain-freq'])

with open(OUTPUT_FILE, 'w') as f:
    f.write(json.dumps(conf, indent=0))
