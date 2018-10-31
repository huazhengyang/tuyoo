# -*- coding=utf-8 -*-
# Author:        luojihui@163.com
# Created:       17/11/15 下午3:15

import random
import freetime.util.log as ftlog
from hall.entity.hallconf import HALL_GAMEID
from poker.entity.configure import configure
from poker.entity.dao import sessiondata
from hall.entity.hallshare import parseClientIdForDL, HallShare

def getShareDownloadUrl(gameId, userId, source):
    clientId = sessiondata.getClientId(userId)
    ok, clientOs, cid, special, mc, sc = parseClientIdForDL(clientId)
    if not ok:
        ftlog.hinfo("getShareDownloadUrl|parseClientId|error", gameId, userId, source, cid, special, mc, sc)
        return

    channels = configure.getGameJson(HALL_GAMEID, "download").get("channels", {})
    channel = clientOs + "." + special + "." + mc + "." + sc

    download = channels["default"]
    if channel in channels:
        download = channels[channel]

    mix_domain = [
    "dspkm.cc",
    "lkxjv.cc",
    "qkpwdfo.cc",
    "sijas.cc",
    "023i.cc",
    "lkjsdf.cc",
    "vdlskm.cc",
    "iojpdvs.cc",
    "sdvnkl.cc",
    "owirhj.cc",
    "lvsdp.cc",
    "msvdkn.cc",
    "dvslkm.cc",
    "odnsvk.cc",
    "p0joefipq.cc",
    "mvsdpok.cc",
    "02r389u.cc",
    "sdlknv.cc",
    "sdfioj.cc",
    "klsdvm.cc"
  ]

    domainList = configure.getGameJson(HALL_GAMEID, "misc").get("mix_domain", mix_domain)
    downloadurl = "http://" + HallShare.randomUrlPrefix() + "." + random.choice(domainList) + download + "?" + "mc=" + mc + "&" + "sc=" + sc + "&" + "cid=" + str(cid) + "&" + "source=" + source

    results = {}
    results["action"] = "geturl"
    results["downloadurl"] = downloadurl

    from freetime.entity.msg import MsgPack
    from poker.protocol import router
    mp = MsgPack()

    mp.setCmd("share_hall")
    mp.setResult("gameId", gameId)
    mp.setResult("userId", userId)
    mp.updateResult(results)
    router.sendToUser(mp, userId)
    if ftlog.is_debug():
        ftlog.debug("getShareDownloadUrl|", gameId, userId, results)


from hall.entity import hallshare
hallshare.getShareDownloadUrl = getShareDownloadUrl