# -*- coding=utf-8 -*-

import re
from urlparse import urlparse, parse_qs

import freetime.util.log as ftlog


comp = re.compile('#途游游戏#您的好友为你准备了(.+?)好礼.+?！(https*://.+)')

class Clipboard(object):
    def __init__(self, content, cmd, url, urlParams):
        self.content = content
        self.cmd = cmd
        self.url = url
        self.urlParams = urlParams
    
    @classmethod
    def parse(cls, content):
        try :
            content = str(content)
            match = comp.search(content)
            if ftlog.is_debug():
                ftlog.debug('Clipboard.parse',
                            'clipboardContent=', content,
                            'match=', len(match.groups()) if match else 0)

            if match and len(match.groups()) >= 2:
                cmd = str(match.group(1))
                url = str(match.group(2))
                parsedUrl = urlparse(url)
                url_query = parse_qs(parsedUrl.query)
                urlParams = dict([(k, v[0]) for k, v in url_query.items()])
                return Clipboard(content, cmd, url, urlParams)
        except:
            ftlog.error('Clipboard.parse failed',
                        'content=', content)
        return None
        

