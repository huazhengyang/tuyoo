# -*- coding: utf-8 -*-
import base64, json, urllib2, urllib

def sendout(posturl, pdatas):
    pass
print '====================================='
purls = ['http://10.3.0.38:10001', 'http://10.3.0.38:10002', 'http://10.3.0.38:10003', 'http://10.3.0.38:10004', 'http://10.3.0.38:10005', 'http://10.3.0.38:10006', 'http://10.3.0.38:10007', 'http://10.3.0.38:10008', 'http://10.3.0.38:10009', 'http://10.3.0.38:10010', 'http://10.3.0.38:10011', 'http://10.3.0.38:10012', 'http://10.3.0.38:10013', 'http://10.3.0.38:10014', 'http://10.3.0.38:10015', 'http://10.3.0.38:10016', 'http://10.3.0.38:10017', 'http://10.3.0.38:10018', 'http://10.3.0.38:10019', 'http://10.3.0.38:10020', 'http://10.3.0.38:10021', 'http://10.3.0.38:10022', 'http://10.3.0.38:10023', 'http://10.3.0.38:10024']
gccode = "\nimport freetime.util.log as ftlog\nftlog.info('hotfix *********** gc.collect in ************************************************')\nimport gc, stackless, types\nftlog.info('hotfix gc.isenabled()=', gc.isenabled())\n#gc.collect()\n\nftlog.info('hotfix *********** gc.collect dump **********************************************')\nobjects = gc.get_objects()\nftlog.info('hotfix gc objects size:', len(objects))\nftlog.info('hotfix current tasklet count:', stackless.getruncount())\ndcinst={}\ndcother={}\nfor o in objects:\n    if hasattr(o, '__class__'):\n        key=str(o.__class__)\n        dc=dcinst\n    else:\n        key=type(o)\n        dc=dcother\n\n    if key in dc:\n        dc[key]+=1\n    else:\n        dc[key]=1\nfor dd in dcinst:\n    ftlog.info('hotfixgc', dd, dcinst[dd])\nfor dd in dcother:\n    ftlog.info('hotfixgc', dd, dcother[dd])\nftlog.info('hotfix *********** gc.collect out ***********************************************')\n"
datas = {'pycode': "\nimport freetime.util.log as ftlog\nftlog.info('hotfix start')\nftlog.info('hotfix end')\n"}
datas['pycode'] = gccode
for x in xrange(len(purls)):
    sendout(purls[x], datas)