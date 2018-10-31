# -*- coding: utf-8 -*-
import redis
import json, traceback
configs = ['server', 'db', 'log_type', 'global']
rs = redis.StrictRedis(host='127.0.0.1', port=7900, db=0)
for c in configs:
    f = (c + '.json')
    print f
    try:
        js = json.loads(open(f, 'r').read())
        jstr = json.dumps(js)
        rs.set(('freetime:' + c), jstr)
    except:
        print 'parse', f, 'error!'
        traceback.print_exc()